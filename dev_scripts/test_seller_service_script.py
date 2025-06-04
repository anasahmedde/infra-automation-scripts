import logging
from seller_service.models import *

logging.disable(logging.INFO)
expired_reactivation_fix_release_date = '2024-06-07' # 07 June, 2024
all_expired_listings = Listing.objects.filter(attributes__status='expired').values_list('id', 'tx_uuid')[:10]
total = len(all_expired_listings)
print("Total Expired Listings:", total)

affected_count = 0
for index, rec in enumerate(all_expired_listings):
         print(index+1, "/", total)
         id, tx_id = rec
         listing = Listing.objects.get(id=id)
         if listing.drafts.exclude(id=listing.tx_uuid).filter(attributes__status='pending_moderation').exists():
            draft = listing.drafts.exclude(id=listing.tx_uuid).order_by('-created_at', '-updated_at').first()
            if draft.status == 'pending_moderation':
                affected_count += 1
                # draft.migrate_taggroup_attributes_to_pk()
                # draft.delete()
print("Affected Drafts:", affected_count)
