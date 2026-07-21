"""Review-only reproducer for the 010N sensitive search authority boundary."""

from unittest.mock import patch

from sfpcl_credit.tests.test_global_search_api import GlobalSearchApiTests


class SensitiveSearchAuthorityProbe(GlobalSearchApiTests):
    def test_cfo_without_blank_cheque_authority_cannot_resolve_owner_by_cheque(self):
        self.assertNotIn(
            "security.package.read",
            self.PERMISSIONS,
            "Probe precondition: actor must lack security-package read authority.",
        )
        self.assertNotIn(
            "security.blank_cheque.manage",
            self.PERMISSIONS,
            "Probe precondition: actor must lack blank-cheque authority.",
        )
        with patch(
            "sfpcl_credit.processes.global_search.BlankDatedCheque.objects.filter"
        ) as restricted_owner:
            restricted_owner.return_value.values_list.return_value = [
                self.member.member_id
            ]
            response = self._search("CHEQUE-SEARCH-001")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["groups"]["members"]["pagination"][
                "total_count"
            ],
            0,
            "FAIL: an actor without blank-cheque authority resolved the cheque's member owner.",
        )
