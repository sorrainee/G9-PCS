from enum import Enum


class Benefit(Enum):
    pass


class RegularBenefit(Benefit):
    HEALTH_INSURANCE = 2000  # Capped to 2k
    DENTAL_INSURANCE = 1000  # Capped to 1k
    VISION_INSURANCE = 1500  # Capped to 1.5k


class PartTimeBenefit(Benefit):
    COMMUTE_INSURANCE = 2000


class CommissionBenefit(Benefit):
    PERFORMANCE_PAY = 3000
