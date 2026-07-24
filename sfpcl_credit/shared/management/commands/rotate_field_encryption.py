from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext
from sfpcl_credit.shared.field_registry import FIELD_ENCRYPTION_MODELS


class Command(BaseCommand):
    help = "Re-encrypt registered sensitive database columns with the active field key."

    def add_arguments(self, parser):
        parser.add_argument("--from-version", required=True)
        parser.add_argument("--batch-size", type=int, default=200)
        parser.add_argument(
            "--resume-after",
            help="Continue after an emitted model-label:primary-key cursor.",
        )

    def handle(self, *args, **options):
        source_version = options["from_version"]
        current_version = FieldEncryption.current_version()
        if source_version == current_version:
            raise CommandError("Source and active field-encryption versions must differ.")
        batch_size = options["batch_size"]
        if batch_size < 1:
            raise CommandError("--batch-size must be positive.")
        resume_model, resume_pk = self._resume_cursor(options.get("resume_after"))
        if resume_model is not None:
            self.stdout.write(f"resumed_after={resume_model}:{resume_pk}")
        counts = {
            "scanned": 0,
            "rotated": 0,
            "already_current": 0,
            "legacy_unrecoverable": 0,
            "legacy_recovered": 0,
        }
        last_cursor = "-"
        resume_reached = resume_model is None

        for spec in FIELD_ENCRYPTION_MODELS:
            if not resume_reached:
                if spec.model_label != resume_model:
                    continue
                resume_reached = True
            model = apps.get_model(spec.model_label)
            queryset = model.objects.order_by(spec.primary_key)
            if spec.model_label == resume_model:
                queryset = queryset.filter(**{f"{spec.primary_key}__gt": resume_pk})
            for row in queryset.iterator(chunk_size=batch_size):
                original_values = {}
                update_values = {}
                for column in spec.columns:
                    token = getattr(row, column.name)
                    if token in (None, ""):
                        continue
                    counts["scanned"] += 1
                    classification, replacement, legacy_recovered = self._rotate_value(
                        token=token,
                        context=column.context,
                        legacy_contexts=column.legacy_contexts,
                        source_version=source_version,
                        current_version=current_version,
                    )
                    counts[classification] += 1
                    if legacy_recovered:
                        counts["legacy_recovered"] += 1
                    if replacement is not None:
                        original_values[column.name] = token
                        update_values[column.name] = replacement
                        if column.hash_name:
                            plaintext = FieldEncryption.decrypt(
                                column.context, replacement
                            )
                            original_values[column.hash_name] = getattr(
                                row, column.hash_name
                            )
                            update_values[column.hash_name] = (
                                FieldEncryption.hash_for_lookup(
                                    column.hash_context, plaintext
                                )
                            )
                if update_values:
                    with transaction.atomic():
                        updated = model.objects.filter(
                            **{
                                spec.primary_key: getattr(row, spec.primary_key),
                                **original_values,
                            }
                        ).update(**update_values)
                    if updated != 1:
                        raise CommandError(
                            "Concurrent field update detected at "
                            f"{spec.model_label}:{getattr(row, spec.primary_key)}; "
                            "rerun from the last successful checkpoint."
                        )
                last_cursor = f"{spec.model_label}:{getattr(row, spec.primary_key)}"
                self.stdout.write(f"checkpoint {last_cursor}")

        if resume_model is not None and not resume_reached:
            raise CommandError("The --resume-after model is not in the encryption registry.")
        self.stdout.write(
            "reconciliation "
            + " ".join(f"{name}={value}" for name, value in counts.items())
        )
        self.stdout.write(f"last_cursor={last_cursor}")

    @staticmethod
    def _rotate_value(
        *, token, context, legacy_contexts, source_version, current_version
    ):
        text = str(token)
        if text.startswith("field:"):
            try:
                token_version = FieldEncryption.key_version(text)
            except InvalidCiphertext as exc:
                raise CommandError(
                    f"Malformed field ciphertext for {context}."
                ) from exc
            if token_version == current_version:
                return "already_current", None, False
            if token_version != source_version:
                raise CommandError(
                    f"Unexpected key version {token_version!r} for {context}."
                )
            plaintext = None
            for read_context in (context, *legacy_contexts):
                try:
                    plaintext = FieldEncryption.decrypt(read_context, text)
                    break
                except InvalidCiphertext:
                    continue
            if plaintext is None:
                raise CommandError(
                    f"Unreadable field ciphertext for {context}."
                )
            return "rotated", FieldEncryption.encrypt(context, plaintext), False
        if text.startswith(("enc:v1:", "seal:v1:")):
            return "legacy_unrecoverable", None, False
        return "rotated", FieldEncryption.encrypt(context, text), True

    @staticmethod
    def _resume_cursor(value):
        if not value:
            return None, None
        try:
            model_label, primary_key = value.rsplit(":", 1)
        except ValueError as exc:
            raise CommandError(
                "--resume-after must be model-label:primary-key."
            ) from exc
        if not model_label or not primary_key:
            raise CommandError("--resume-after must be model-label:primary-key.")
        return model_label, primary_key
