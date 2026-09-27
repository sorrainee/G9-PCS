from enum import Enum


class Benefit(Enum):
    pass


class RegularBenefit(Benefit):
    HEALTH_INSURANCE = 10000
    DENTAL_INSURANCE = 8000
    VISION_INSURANCE = 7000


class PartTimeBenefit(Benefit):
    PAID_TIME_OFF = 4000
    COMMUTE_INSURANCE = 2000


class CommissionBenefit(Benefit):
    PERFORMANCE_PAY = 3000
