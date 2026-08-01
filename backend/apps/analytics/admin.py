from django.contrib import admin

# As per project engineering standards and requirements, apps.analytics is purely
# a read-only business aggregation and reporting module operating over existing
# domain tables (Accounts, Campaigns, Donations, Payouts, Beneficiaries, Milestones,
# Execution Partners, and Notifications). Therefore, no dedicated database tables
# exist or are registered in the Django Admin Portal for this package.
