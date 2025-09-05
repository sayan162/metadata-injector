import streamlit as st
import os
import random
import sys
import subprocess

# Install mutagen if not present
try:
    from mutagen import File
    from mutagen.mp4 import MP4
    from mutagen.asf import ASF
except ImportError:
    st.write("Installing mutagen library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen"])
    from mutagen import File
    from mutagen.mp4 import MP4
    from mutagen.asf import ASF

# Sample metadata pools with realistic comments
TITLES = [
    "Sunset Dreams", "Midnight Journey", "Ocean Waves", "Mountain Echo", "Urban Lights",
    "Forest Whispers", "Desert Mirage", "Arctic Silence", "Tropical Breeze", "Cosmic Voyage",
    "Ancient Ruins", "Neon Nights", "Golden Hour", "Crystal Clear", "Electric Dreams",
    "Silent Storm", "Frozen Time", "Wildfire", "Stellar Wind", "Mystic Shadows"
]

ARTISTS = [
    "Alex Rivers", "Sam Phoenix", "Jordan Blake", "Casey Storm", "Morgan Reed",
    "Riley Stone", "Quinn Frost", "Avery Lane", "Drew Sky", "Jamie Moon",
    "Taylor Swift", "Chris Martin", "Billie Eilish", "Ed Sheeran", "Ariana Grande",
    "The Weeknd", "Dua Lipa", "Bruno Mars", "Lady Gaga", "Justin Bieber"
]

ALBUMS = [
    "Horizons", "Reflections", "Euphoria", "Chronicles", "Odyssey",
    "Serenity", "Velocity", "Momentum", "Harmony", "Paradox",
    "Infinity", "Legacy", "Nexus", "Apex", "Zenith",
    "Voyage", "Odyssey", "Genesis", "Revelation", "Ascension"
]

GENRES = [
    "Electronic", "Rock", "Pop", "Hip-Hop", "Classical",
    "Jazz", "Ambient", "Soundtrack", "World", "Experimental",
    "R&B", "Country", "Folk", "Blues", "Reggae",
    "Metal", "Punk", "Indie", "Alternative", "Dance"
]

COMMENTS = [
    "Enjoy this video!", "Hope you like this content", "Thanks for watching",
    "Created with passion", "Made for entertainment", "Share if you enjoyed",
    "Watch in HD for best experience", "Subscribe for more content",
    "Like and comment below", "Follow for updates", "Turn up the volume!",
    "Best viewed in fullscreen", "Thanks for your support", "Stay tuned",
    "More coming soon", "Hit the like button", "Don't forget to share"
]

def generate_random_metadata():
    return {
        "title": random.choice(TITLES),
        "artist": random.choice(ARTISTS),
        "album": random.choice(ALBUMS),
        "year": str(random.randint(1990, 2023)),
        "comment": random.choice(COMMENTS),
        "genre": random.choice(GENRES),
        "track": str(random.randint(1, 20))
    }

def inject_metadata(file_path):
    metadata = generate_random_metadata()
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # Use universal File handler for most formats
        if file_ext not in (".mp4", ".asf", ".wmv"):
            audio_file = File(file_path, easy=True)
            if audio_file:
                audio_file['title'] = metadata["title"]
                audio_file['artist'] = metadata["artist"]
                audio_file['album'] = metadata["album"]
                audio_file['date'] = metadata["year"]
                audio_file['comment'] = metadata["comment"]
                audio_file['genre'] = metadata["genre"]
                audio_file['tracknumber'] = metadata["track"]
                audio_file.save()
                return metadata
        
        # Format-specific handling
        if file_ext == ".mp4":
            audio_file = MP4(file_path)
            audio_file["\xa9nam"] = metadata["title"]
            audio_file["\xa9ART"] = metadata["artist"]
            audio_file["\xa9alb"] = metadata["album"]
            audio_file["\xa9day"] = metadata["year"]
            audio_file["\xa9cmt"] = metadata["comment"]
            audio_file["\xa9gen"] = metadata["genre"]
            audio_file["trkn"] = [(int(metadata["track"]), 20)]
            audio_file.save()
            return metadata
            
        elif file_ext in (".wmv", ".asf"):
            audio_file = ASF(file_path)
            audio_file["Title"] = metadata["title"]
            audio_file["Author"] = metadata["artist"]
            audio_file["WM/AlbumTitle"] = metadata["album"]
            audio_file["WM/Year"] = metadata["year"]
            audio_file["Description"] = metadata["comment"]
            audio_file["WM/Genre"] = metadata["genre"]
            audio_file["WM/TrackNumber"] = int(metadata["track"])
            audio_file.save()
            return metadata
            
        else:
            st.error(f"Unsupported format: {file_ext}")
            return None
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Page configuration
st.set_page_config(
    page_title="Video Metadata Injector",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Main content
st.title("🎬 Random Video Metadata Injector")
st.markdown("---")
st.write("Upload a video file to inject random metadata. Supports MP4, MKV, WMV, and ASF formats.")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a video file",
    type=["mp4", "mkv", "wmv", "asf"],
    help="Select a video file from your device"
)

if uploaded_file is not None:
    # Display file details
    file_details = {
        "Filename": uploaded_file.name,
        "File type": uploaded_file.type,
        "File size": f"{uploaded_file.size / 1024 / 1024:.2f} MB"
    }
    st.write("### File Details")
    st.json(file_details)
    
    # Save the uploaded file temporarily
    temp_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Inject metadata
    with st.spinner("Injecting metadata..."):
        metadata = inject_metadata(temp_path)
    
    if metadata:
        st.success("✅ Metadata injected successfully!")
        st.write("### New Metadata")
        
        # Create a nice display for metadata
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {metadata['title']}")
            st.markdown(f"**Artist:** {metadata['artist']}")
            st.markdown(f"**Album:** {metadata['album']}")
            st.markdown(f"**Year:** {metadata['year']}")
        with col2:
            st.markdown(f"**Genre:** {metadata['genre']}")
            st.markdown(f"**Track:** {metadata['track']}")
            st.markdown(f"**Comment:** {metadata['comment']}")
        
        # Provide download button
        st.markdown("---")
        st.write("### Download Processed Video")
        with open(temp_path, "rb") as f:
            st.download_button(
                label="💾 Download Processed Video",
                data=f,
                file_name=f"processed_{uploaded_file.name}",
                mime="video/mp4",
                help="Click to download the video with new metadata"
            )
        
        # Additional info
        st.info("💡 The metadata has been permanently added to your video file. You can verify it in any media player that shows metadata.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Made with ❤️ using Streamlit | 
        <a href='https://github.com' target='_blank'>GitHub</a> | 
        <a href='https://streamlit.io' target='_blank'>Streamlit</a>
    </div>
    """,
    unsafe_allow_html=True
)
