import xml.etree.ElementTree as ET
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

CLEANED_CSV_FILE_PATH = 'cleaned_file.csv' 

KEYS_TO_DROP = [
    'Track ID', 'Kind',
    'Disc Number', 'Disc Count', 'Track Number', 'Track Count', 'Genre',
    'Playlist Only', 'Sort Album Artist','Album Artist','Sort Artist',
    'Date Modified', 'Bit Rate', 'Movement Count', 'Movement Number',
    'Play Date', 'Play Date UTC', 'Grouping',
    'Skip Count', 'Skip Date', 'Normalization',
    'Compilation', 'Sort Album', 
    'Sort Composer', 'Sort Name', 'Persistent ID',
    'Track Type', 'Purchased','Location', 
    'File Folder Count', 'Library Folder Count', 
    'Apple Music', 'Artwork Count', 'Date Added', 'Work',
    'Comments', 'Movement Name', 'Clean', 'Favorited', 'Loved',
    'Size', 'Play Count', 'Total Time', 'Release Date', 'Composer', 'Explicit', 'Part Of Gapless Album',
    'Year', 'Sample Rate', 'Album'
]

def load_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except Exception as e:
        print(f"Error loading XML file: {e}")
        return None

def extract_first_dict(root):
    tracks_found = False
    
    for element in root.iter():
        if element.tag == "key" and element.text == "Tracks":
            tracks_found = True  
        elif tracks_found and element.tag == "dict":
            return element  

    return None

def parse_dict(element):
    songs_data = []
    
    def process_single_dict(dict_elem):
        song_data = {}
        key = None
        for child in dict_elem:
            if child.tag == 'key':
                key = child.text  
            elif key:
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

    for track in element.findall("dict"):
        songs_data.append(process_single_dict(track))
    
    return songs_data

def write_to_cleaned_csv(songs_data, output_file_path):
    if not songs_data:
        print("No song data available to write.")
        return

    df = pd.DataFrame(songs_data)  
    
    df.drop(columns=KEYS_TO_DROP, errors='ignore', inplace=True)

    if 'Artist' in df.columns:
        def clean_artist(artist):
            if not isinstance(artist, str):
                return artist  
            
            artist = artist.replace("Namedarumaaz", "Namedaruma")
            
            artist = artist.replace(" &", ",")
            artist = artist.replace("&", ",")
            artist = artist.split(',')[0].strip()
            artist = artist.split('loves')[0].strip()

            remove_words = ['feat.', 'Feat.', 'FEAT.', 'featuring']
            
            for word in remove_words:
                artist = artist.replace(f" {word}", " ").replace(f"{word} ", "").replace(word, "")
            
            return artist.strip()
        
        df['Artist'] = df['Artist'].apply(clean_artist)

    if 'Name' in df.columns:
        def clean_name(name):
            if not isinstance(name, str):
                return name  
            
            if not name.startswith('('):
                name = name.split('(')[0].strip()
            
            name = name.split("/")[0].strip()
            name = name.split(" - ")[0].strip()
            
            remove_words = ['feat.', 'Feat.', 'FEAT.', 'featuring']
            
            for word in remove_words:
                name = name.replace(f" {word}", " ").replace(f"{word} ", "").replace(word, "")
            
            return name.strip()
        
        df['Name'] = df['Name'].apply(clean_name)

    df['Spotify URI'] = None

    df.to_csv(output_file_path, index=False)
    print(f"Data written to '{output_file_path}' successfully.")
    
def load_process_and_save(xml_file_path):
    root = load_xml_file(xml_file_path)
    if root is not None:
        first_dict = extract_first_dict(root)
        if first_dict is not None:
            songs_data = parse_dict(first_dict)  
            write_to_cleaned_csv(songs_data, CLEANED_CSV_FILE_PATH)
        else:
            print("First <dict> not found.")
    else:
        print("Failed to extract data from XML.")

if __name__ == "__main__":
    load_process_and_save("playlist.xml")
