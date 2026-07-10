"""Public entry seam for appraisal behavior delivered by slices 006E-006G."""


class AppraisalWorkflow:
    def create_or_update(self, *, actor, application_id, payload):
        raise NotImplementedError("Appraisal workflow is owned by slice 006E.")

    def submit_for_review(self, *, actor, appraisal_id):
        raise NotImplementedError("Appraisal workflow is owned by slice 006E.")

    def review(self, *, actor, appraisal_id, decision, comments):
        raise NotImplementedError("Appraisal review is owned by slice 006F.")

    def submit_to_sanction(self, *, actor, application_id):
        raise NotImplementedError("Sanction submission is owned by slice 006G.")
