from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from analytics.filters import (
    DateRangeStrategy,
    SameDayOverlapStrategy,
    SupervisionDateFilter,
)
from analytics.models import Supervision
from core.models import Organization
from users.models import User


class SupervisionDateFilterTestCase(TestCase):
    """Test cases for SupervisionDateFilter."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.filter = SupervisionDateFilter()
        
        # Create test users and organization
        self.organization = Organization.objects.create(name="Test Org")
        self.worker = User.objects.create_user(
            username="worker",
            email="worker@test.com",
            password="testpass"
        )
        self.supervisor = User.objects.create_user(
            username="supervisor",
            email="supervisor@test.com",
            password="testpass"
        )
        
        # Create supervisions with different date ranges
        today = timezone.now()
        
        # Supervision 1: Jan 1-5, 2024
        self.supervision1 = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 1, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 5, 15, 0)),
        )
        
        # Supervision 2: Jan 3, 2024 (same day start and end)
        self.supervision2 = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 3, 9, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 3, 17, 0)),
        )
        
        # Supervision 3: Jan 6-10, 2024
        self.supervision3 = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 6, 8, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 10, 16, 0)),
        )
        
        # Supervision 4: Jan 2, 2024 (ongoing - no end_date)
        self.supervision4 = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 2, 12, 0)),
            end_date=None,
        )
        
        # Supervision 5: Dec 30, 2023 - Jan 2, 2024 (spans across date range)
        self.supervision5 = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2023, 12, 30, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 2, 14, 0)),
        )
        
        self.queryset = Supervision.objects.all()

    def test_no_date_parameters(self):
        """Test that filter returns all supervisions when no date parameters provided."""
        request = self.factory.get("/api/supervisions/")
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 5)

    def test_same_day_filtering_overlap(self):
        """Test same day filtering with overlap logic."""
        # Filter for Jan 3, 2024 - should return supervision2 (started and ended on that day)
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-03", "end_date": "2024-01-03"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.supervision2, filtered)

    def test_same_day_filtering_ongoing(self):
        """Test same day filtering includes ongoing supervisions."""
        # Filter for Jan 2, 2024 - should return supervision4 (ongoing) and supervision5 (ended on that day)
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-02", "end_date": "2024-01-02"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 2)
        self.assertIn(self.supervision4, filtered)
        self.assertIn(self.supervision5, filtered)

    def test_same_day_filtering_started_before(self):
        """Test same day filtering includes supervisions that started before but ended on the date."""
        # Filter for Jan 5, 2024 - should return supervision1 (ended on that day)
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-05", "end_date": "2024-01-05"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.supervision1, filtered)

    def test_date_range_filtering(self):
        """Test date range filtering where both dates fall within range."""
        # Filter for Jan 1-5, 2024 - should return supervision1 and supervision2
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-01", "end_date": "2024-01-05"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 2)
        self.assertIn(self.supervision1, filtered)
        self.assertIn(self.supervision2, filtered)

    def test_date_range_filtering_includes_ongoing(self):
        """Test date range filtering includes ongoing supervisions if start_date is within range."""
        # Filter for Jan 1-5, 2024 - should include supervision4 (ongoing, started on Jan 2)
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-01", "end_date": "2024-01-05"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertIn(self.supervision4, filtered)

    def test_date_range_filtering_single_supervision(self):
        """Test date range filtering with a range that matches one supervision exactly."""
        # Filter for Jan 6-10, 2024 - should return only supervision3
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-06", "end_date": "2024-01-10"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.supervision3, filtered)

    def test_only_start_date_provided(self):
        """Test that only start_date uses same day filtering."""
        request = self.factory.get("/api/supervisions/", {"start_date": "2024-01-03"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.supervision2, filtered)

    def test_only_end_date_provided(self):
        """Test that only end_date uses same day filtering."""
        request = self.factory.get("/api/supervisions/", {"end_date": "2024-01-03"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.supervision2, filtered)

    def test_invalid_start_date(self):
        """Test that invalid start_date returns empty queryset."""
        request = self.factory.get("/api/supervisions/", {"start_date": "invalid-date"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 0)

    def test_invalid_end_date(self):
        """Test that invalid end_date returns empty queryset."""
        request = self.factory.get("/api/supervisions/", {"end_date": "invalid-date"})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 0)

    def test_empty_date_parameters(self):
        """Test that empty date parameters are handled."""
        request = self.factory.get("/api/supervisions/", {"start_date": "", "end_date": ""})
        filtered = self.filter.filter_queryset(request, self.queryset, None)
        
        self.assertEqual(filtered.count(), 5)


class SameDayOverlapStrategyTestCase(TestCase):
    """Test cases for SameDayOverlapStrategy."""

    def setUp(self):
        """Set up test data."""
        self.strategy = SameDayOverlapStrategy()
        self.organization = Organization.objects.create(name="Test Org")
        self.worker = User.objects.create_user(
            username="worker",
            email="worker@test.com",
            password="testpass"
        )
        self.supervisor = User.objects.create_user(
            username="supervisor",
            email="supervisor@test.com",
            password="testpass"
        )

    def test_filter_supervision_active_on_date(self):
        """Test filtering supervisions active on a specific date."""
        # Create supervision that spans the date
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 1, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 5, 15, 0)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 3), date(2024, 1, 3))
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(supervision, filtered)

    def test_filter_ongoing_supervision(self):
        """Test filtering includes ongoing supervisions."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 1, 10, 0)),
            end_date=None,
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 5), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(supervision, filtered)

    def test_filter_excludes_supervision_started_after(self):
        """Test filtering excludes supervisions that started after the date."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 5, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 10, 15, 0)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 3), date(2024, 1, 3))
        
        self.assertEqual(filtered.count(), 0)
        self.assertNotIn(supervision, filtered)

    def test_filter_excludes_supervision_ended_before(self):
        """Test filtering excludes supervisions that ended before the date."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 1, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 2, 15, 0)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 5), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 0)
        self.assertNotIn(supervision, filtered)


class DateRangeStrategyTestCase(TestCase):
    """Test cases for DateRangeStrategy."""

    def setUp(self):
        """Set up test data."""
        self.strategy = DateRangeStrategy()
        self.organization = Organization.objects.create(name="Test Org")
        self.worker = User.objects.create_user(
            username="worker",
            email="worker@test.com",
            password="testpass"
        )
        self.supervisor = User.objects.create_user(
            username="supervisor",
            email="supervisor@test.com",
            password="testpass"
        )

    def test_filter_supervision_within_range(self):
        """Test filtering supervisions where both dates fall within range."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 2, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 4, 15, 0)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 1), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(supervision, filtered)

    def test_filter_excludes_supervision_started_before_range(self):
        """Test filtering excludes supervisions that started before the range."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2023, 12, 30, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 4, 15, 0)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 1), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 0)
        self.assertNotIn(supervision, filtered)

    def test_filter_excludes_supervision_ended_after_range(self):
        """Test filtering excludes supervisions that ended after the range."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 2, 10, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 10, 15, 0)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 1), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 0)
        self.assertNotIn(supervision, filtered)

    def test_filter_includes_ongoing_supervisions(self):
        """Test filtering includes ongoing supervisions (no end_date) if start_date is within range."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 2, 10, 0)),
            end_date=None,
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 1), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(supervision, filtered)

    def test_filter_exact_range_match(self):
        """Test filtering with exact range match."""
        supervision = Supervision.objects.create(
            worker=self.worker,
            organization=self.organization,
            user=self.supervisor,
            start_date=timezone.make_aware(datetime(2024, 1, 1, 0, 0)),
            end_date=timezone.make_aware(datetime(2024, 1, 5, 23, 59)),
        )
        
        queryset = Supervision.objects.all()
        filtered = self.strategy.filter(queryset, date(2024, 1, 1), date(2024, 1, 5))
        
        self.assertEqual(filtered.count(), 1)
        self.assertIn(supervision, filtered)
