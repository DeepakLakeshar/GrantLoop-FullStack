from django.contrib import admin

# As per project architectural guidelines and engineering standards, apps.reports
# functions strictly as a read-only reporting and file export generation engine
# operating over existing domain models (Accounts, Campaigns, Donations, Payouts,
# Beneficiaries, Milestones, and Analytics aggregations). Therefore, no dedicated
# database tables exist or are registered in the Django Admin Portal for this module.
