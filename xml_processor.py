import xml.etree.ElementTree as ET
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

# Define your file paths here               # Path to your XML file
CLEANED_CSV_FILE_PATH = 'cleaned_file.csv'    # Output path for cleaned CSV file

# List of keys (columns) to drop from the DataFrame
KEYS_TO_DROP = [
    'Track ID', 'Kind',
    'Disc Number', 'Disc Count', 'Track Number', 'Track Count', 'Genre',
    'Playlist Only', 'Sort Album Artist', 'Artist',
    'Date Modified', 'Bit Rate', 'Movement Count', 'Movement Number',
    'Play Date', 'Play Date UTC', 'Grouping',
    'Skip Count', 'Skip Date', 'Normalization',
    'Compilation', 'Sort Album', 'Sort Artist', 
    'Sort Composer', 'Sort Name', 'Persistent ID',
    'Track Type', 'Purchased', 'Location', 
    'File Folder Count', 'Library Folder Count', 
    'Apple Music', 'Artwork Count', 'Date Added', 'Work',
    'Comments', 'Movement Name', 'Clean', 'Favorited', 'Loved',
    'Size', 'Play Count', 'Total Time', 'Release Date', 'Composer', 'Explicit', 'Part Of Gapless Album',
    'Year', 'Album', 'Sample Rate'
]

# Load XML from a file
def load_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except Exception as e:
        print(f"Error loading XML file: {e}")
        return None

# Extract the first <dict> tag under <key>Tracks</key>
def extract_first_dict(root):
    tracks_found = False
    
    for element in root.iter():
        if element.tag == "key" and element.text == "Tracks":
            tracks_found = True  # Mark that we've found Tracks
        elif tracks_found and element.tag == "dict":
            return element  # Return the first <dict> after Tracks

    return None

# Parse the <dict> element to extract song data
def parse_dict(element):
    songs_data = []
    
    # Function to process each <dict> element and extract key-value pairs
    def process_single_dict(dict_elem):
        song_data = {}
        key = None
        for child in dict_elem:
            if child.tag == 'key':
                key = child.text  # Store the key text
            elif key:
                # Store value based on tag type in a flat dictionary for CSV compatibility
                if child.tag == 'integer':
                    song_data[key] = int(child.text)
                elif child.tag == 'string':
                    song_data[key] = child.text
                elif child.tag == 'date':
                    song_data[key] = child.text
                elif child.tag == 'true':
                    song_data[key] = True
                elif child.tag == 'false':
                    song_data[key] = False
                key = None
        return song_data

    # Iterate through all <dict> elements (each represents a track)
    for track in element.findall("dict"):
        songs_data.append(process_single_dict(track))
    
    return songs_data

# Write song data to a cleaned CSV file
def write_to_cleaned_csv(songs_data, output_file_path):
    if not songs_data:
        print("No song data available to write.")
        return

    df = pd.DataFrame(songs_data)  # Create DataFrame from songs data
    
    # Drop specified keys (columns) from the DataFrame
    df.drop(columns=KEYS_TO_DROP, errors='ignore', inplace=True)

    # Filling NaNs with the mean of the column
    # df['Album'] = df['Album'].str.title()
    # df['Genre'] = df['Genre'].str.title()
    # df['Size'] = df['Size'].fillna(df['Size'].mean())
    # df['Play Count'] = df['Play Count'].fillna(0)
    # df['Total Time'] = df['Total Time'].fillna(df['Total Time'].mean())
    # df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
    # df['Composer'] = df['Composer'].fillna('Unknown')
    # df['Explicit'] = df['Explicit'].astype('boolean').fillna(False)
    # df['Part Of Gapless Album'] = df['Part Of Gapless Album'].astype('boolean').fillna(False)
    # df['Year'] = df['Year'].ffill()  # Fill missing values with the last valid observation
    # df['Release Date'] = df['Release Date'].ffill() 
    # missing_data = df.isnull().sum()
    # print(missing_data)
    

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv(output_file_path, index=False)
    print(f"Data written to '{output_file_path}' successfully.")

# Main function to load XML, extract the first <dict>, parse, and write to CSV
def load_process_and_save(xml_file_path):
    root = load_xml_file(xml_file_path)
    if root is not None:
        first_dict = extract_first_dict(root)
        if first_dict is not None:
            # Parse the first dict directly and write data to CSV
            songs_data = parse_dict(first_dict)  # Pass the first <dict> element
            write_to_cleaned_csv(songs_data, CLEANED_CSV_FILE_PATH)
        else:
            print("First <dict> not found.")
    else:
        print("Failed to extract data from XML.")

if __name__ == "__main__":
    load_process_and_save("playlist.xml")
