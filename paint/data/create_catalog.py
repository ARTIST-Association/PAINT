import os
from datetime import datetime
import pystac

def create_empty_stac_file(stac_file_path):
    # Create a new Catalog
    catalog = pystac.Catalog(id='solar_tower_catalog',
                             description='Catalog for Solar Tower Heliostats',
                             title='Solar Tower Catalog')

    # Save the Catalog to a STAC file
    catalog.normalize_and_save(stac_file_path, catalog_type=pystac.CatalogType.SELF_CONTAINED)

    return catalog

def add_heliostat_collections(catalog, num_heliostats):
    # Create a Collection for each heliostat
    for i in range(1, num_heliostats + 1):
        heliostat_collection = pystac.Collection(
            id=f'heliostat_{i}',
            description=f'Heliostat {i} Collection',
            title=f'Heliostat {i}',
            extent=None  # You can specify the extent if needed
        )
        catalog.add_child(heliostat_collection)

    # Save the updated Catalog
    catalog.save(catalog.get_self_href())

def add_subcollections_to_heliostat(catalog, heliostat_id, subcollection_names):
    # Find the heliostat Collection by ID
    heliostat_collection = catalog.get_child(f'heliostat_{heliostat_id}')

    # Create subcollections under the heliostat Collection
    for subcollection_name in subcollection_names:
        subcollection = pystac.Collection(
            id=f'{heliostat_collection.id}/{subcollection_name}',
            description=f'Subcollection {subcollection_name} for Heliostat {heliostat_id}',
            title=subcollection_name,
            extent=None  # You can specify the extent if needed
        )
        heliostat_collection.add_child(subcollection)

    # Save the updated Catalog
    catalog.save(catalog.get_self_href())

if __name__ == "__main__":
    # Path to save the STAC file
    stac_file_path = 'solar_tower_catalog.stac.json'

    # Create an empty STAC file
    catalog = create_empty_stac_file(stac_file_path)

    # Add heliostat Collections
    num_heliostats = 2000
    add_heliostat_collections(catalog, num_heliostats)

    # Example: Add subcollections for a specific heliostat (e.g., heliostat 1)
    heliostat_id = 1
    subcollection_names = ['subcollection1', 'subcollection2', 'subcollection3']
    add_subcollections_to_heliostat(catalog, heliostat_id, subcollection_names)

    print(f"STAC file created and populated: {stac_file_path}")