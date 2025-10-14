from core.tests_base.test_admin import TestAdminBase


class RouletteAdminTestCase(TestAdminBase):
    """Testing company admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/roulette/roulette/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class AwardAdminTestCase(TestAdminBase):
    """Testing award admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/roulette/award/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class ParticipantAdminTestCase(TestAdminBase):
    """Testing participant admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/roulette/participant/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class ParticipantSpinAdminTestCase(TestAdminBase):
    """Testing participant spin admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/roulette/participantspin/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class ParticipantAwardAdminTestCase(TestAdminBase):
    """Testing participant award admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/roulette/participantaward/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)
