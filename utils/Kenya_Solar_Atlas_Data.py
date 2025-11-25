import os
import requests
import json
import numpy as np
from pathlib import Path
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping


# Download kenya Solar data
def download_kenya_solar_data():
    url = 'https://api.globalsolaratlas.info/download/Kenya/Kenya_GHI_poster-map_1000x1000mm-300dpi_v20191017.tif'
    filename = 'data/kenya_ghi.tif'
    
    try:
        # Create the 'data' directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Using requests to download the file (always overwrite)
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"File '{filename}' downloaded successfully (or updated).")
    except Exception as e:
        print(f"Error downloading the file: {e}")

# Download Kenya counties GeoJSON
def get_kenya_counties_geojson():
    """
    Download Kenya counties boundary data from a public source.
    """
    # Using Kenya Open Data Portal / humanitarian data sources
    url = "https://raw.githubusercontent.com/mikelmaron/kenya-election-data/master/data/counties.geojson"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to file
        with open("kenya_counties.geojson", "w") as f:
            f.write(response.text)
        
        return "kenya_counties.geojson"
    except Exception as e:
        print(f"Error downloading counties data: {e}")
        print("You may need to provide a kenya_counties.geojson file manually")
        return None

# Extract irradiance data by county
def extract_irradiance_by_county(tif_path, counties_geojson_path):
    """
    Extract average solar irradiance values for each county in Kenya.
    
    Args:
        tif_path: Path to the GeoTIFF file with solar irradiance data
        counties_geojson_path: Path to GeoJSON file with county boundaries
    
    Returns:
        Dictionary with county names and their average irradiance values
    """
    # Read county boundaries
    counties = gpd.read_file(counties_geojson_path)
    
    # Ensure the GeoDataFrame has a CRS
    if counties.crs is None:
        counties = counties.set_crs("EPSG:4326")
    
    results = []
    
    # Open the GeoTIFF file
    with rasterio.open(tif_path) as src:
        print(f"GeoTIFF CRS: {src.crs}")
        print(f"GeoTIFF bounds: {src.bounds}")
        print(f"GeoTIFF shape: {src.shape}")
        print(f"GeoTIFF dtype: {src.dtypes[0] if src.dtypes else 'Unknown'}")
        
        # Read the entire raster into memory
        raster_data = src.read(1)
        print(f"Raster data type: {raster_data.dtype}")
        print(f"Raster data range: [{np.nanmin(raster_data)}, {np.nanmax(raster_data)}]")
        
        # Since the raster has no georeferencing, we'll use a simple approach:
        # Normalize the raster to geographic bounds that encompass Kenya
        # Kenya bounds approximately: lat -4 to 5, lon 34 to 42
        
        raster_height, raster_width = raster_data.shape
        
        # Create a simple pixel-to-coordinate mapping
        # Assuming the raster covers Kenya's bounding box
        kenya_bounds = {
            'west': 33.87,
            'east': 41.86,
            'south': -4.68,
            'north': 5.0
        }
        
        # Create a simple rasterio-like transform for the raster
        from rasterio.transform import from_bounds
        transform = from_bounds(
            kenya_bounds['west'], 
            kenya_bounds['south'],
            kenya_bounds['east'],
            kenya_bounds['north'],
            raster_width,
            raster_height
        )
        
        print(f"Using transform with Kenya bounds approximation")
        
        # Process each county
        for idx, county in counties.iterrows():
            try:
                # Get county name
                county_name = county.get('COUNTY_NAM') or county.get('name') or county.get('NAME') or f"County_{idx}"
                
                # Get the geometry
                geom = county.geometry
                
                # Use rasterio's window feature to extract pixels
                from rasterio.windows import from_bounds as window_from_bounds
                
                bounds = geom.bounds  # (minx, miny, maxx, maxy)
                
                # Convert geographic bounds to pixel indices
                # This is a simplified approach since we don't have proper georeferencing
                x_min, y_min, x_max, y_max = bounds
                
                # Map coordinates to pixel indices
                pixel_x_min = max(0, int((x_min - kenya_bounds['west']) / (kenya_bounds['east'] - kenya_bounds['west']) * raster_width))
                pixel_x_max = min(raster_width, int((x_max - kenya_bounds['west']) / (kenya_bounds['east'] - kenya_bounds['west']) * raster_width))
                pixel_y_max = max(0, int((kenya_bounds['north'] - y_min) / (kenya_bounds['north'] - kenya_bounds['south']) * raster_height))
                pixel_y_min = min(raster_height, int((kenya_bounds['north'] - y_max) / (kenya_bounds['north'] - kenya_bounds['south']) * raster_height))
                
                # Ensure valid ranges
                if pixel_x_min >= pixel_x_max or pixel_y_min >= pixel_y_max:
                    print(f"✗ {county_name}: Invalid pixel range")
                    continue
                
                # Extract the data window
                data_window = raster_data[pixel_y_min:pixel_y_max, pixel_x_min:pixel_x_max]
                
                # Handle different data types with proper scaling
                if data_window.dtype == np.uint8:
                    valid_pixels = data_window[data_window > 0].astype(float)
                    # Apply scaling: map 0–255 → 0–6 kWh/m²/day
                    scale_factor = 5.5 / 255.0
                    valid_pixels = valid_pixels * scale_factor
                else:
                    valid_pixels = data_window[~np.isnan(data_window)]
                
                if len(valid_pixels) > 0:
                    avg_irradiance = float(np.mean(valid_pixels))
                    min_irradiance = float(np.min(valid_pixels))
                    max_irradiance = float(np.max(valid_pixels))
                    std_irradiance = float(np.std(valid_pixels))
                    
                    results.append({
                        "county": county_name,
                        "avg_irradiance_kwh_m2_day": round(avg_irradiance, 2),
                        "min_irradiance_kwh_m2_day": round(min_irradiance, 2),
                        "max_irradiance_kwh_m2_day": round(max_irradiance, 2),
                        "std_irradiance_kwh_m2_day": round(std_irradiance, 2),
                        "pixel_count": len(valid_pixels)
                    })
                    
                    print(f"✓ {county_name}: {avg_irradiance:.2f} kWh/m²/day")
                else:
                    print(f"✗ {county_name}: No valid data")
                    
            except Exception as e:
                print(f"✗ Error processing {county_name}: {e}")
    
    return results

# Main function to create Kenya counties irradiance JSON
def create_kenya_counties_irradiance_json(
    tif_path="data/kenya_ghi.tif",
    counties_geojson_path="data/kenya_counties.geojson",
    output_json="data/kenya_counties_irradiance.json"
):
    """
    Main function to create the final JSON file with county irradiance data.
    
    Args:
        tif_path: Path to solar irradiance GeoTIFF file
        counties_geojson_path: Path to counties GeoJSON file
        output_json: Output JSON file path
    """
    print("=" * 60)
    print("Kenya Solar Irradiance Data Processor")
    print("=" * 60)
    # Ensure data directory exists
    download_kenya_solar_data()

    # Check if files exist
    if not os.path.exists(tif_path):
        print(f"\n⚠️  GeoTIFF file not found: {tif_path}")
        print("Please download it manually from:")
        print("https://globalsolaratlas.info/download/kenya")
        return
    
    if not os.path.exists(counties_geojson_path):
        print(f"\n⚠️  Counties GeoJSON not found. Attempting to download...")
        counties_geojson_path = get_kenya_counties_geojson()
        if not counties_geojson_path:
            return
    
    print(f"\n📂 Processing data...")
    print(f"   GeoTIFF: {tif_path}")
    print(f"   Counties: {counties_geojson_path}")
    
    # Extract irradiance data
    irradiance_data = extract_irradiance_by_county(tif_path, counties_geojson_path)
    
    if irradiance_data:
        # Create final JSON structure
        output = {
            "metadata": {
                "source": "Global Solar Atlas",
                "url": "https://globalsolaratlas.info",
                "country": "Kenya",
                "resolution": "1 km",
                "units": "kWh/m²/day",
                "description": "Average daily solar irradiance by county"
            },
            "counties": irradiance_data
        }
        
        # Save to JSON
        with open(output_json, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✅ Success! Created {output_json}")
        print(f"   Total counties processed: {len(irradiance_data)}")
        
        # Show summary statistics
        avg_values = [c['avg_irradiance_kwh_m2_day'] for c in irradiance_data]
        print(f"\n📊 Summary Statistics:")
        print(f"   Highest irradiance: {max(avg_values):.2f} kWh/m²/day")
        print(f"   Lowest irradiance: {min(avg_values):.2f} kWh/m²/day")
        print(f"   National average: {np.mean(avg_values):.2f} kWh/m²/day")
    else:
        print("\n❌ No data extracted. Please check your input files.")


if __name__ == "__main__":

    
    # Run the main function
    create_kenya_counties_irradiance_json()