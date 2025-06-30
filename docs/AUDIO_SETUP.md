# 🎵 Snake Game Ultimate - Audio Setup Guide

## Quick Start
The game will run immediately with built-in placeholder sounds! For the best experience, follow the setup below to add professional audio.

## 📁 Audio File Structure
Create this folder structure in your game directory:

```
amazon-q-game/
├── snake_game_audio.py
├── audio/
│   ├── background_music.ogg     # Looping background music
│   ├── eat_food.wav            # Snake eating sound
│   ├── turn.wav                # Direction change sound
│   ├── game_over.wav           # Game over sound
│   ├── button_hover.wav        # Button hover sound
│   ├── button_click.wav        # Button click sound
│   └── game_start.wav          # Game start sound
```

## 🎼 Recommended Royalty-Free Audio Sources

### Background Music (OGG format recommended)
- **Freesound.org** - Search: "ambient loop", "game music", "electronic loop"
- **OpenGameArt.org** - Extensive free game music collection
- **Zapsplat.com** - Professional quality (free with registration)
- **YouTube Audio Library** - Download MP3, convert to OGG
- **Incompetech.com** - Kevin MacLeod's royalty-free music

### Sound Effects (WAV format recommended)
- **Freesound.org** - Search terms:
  - "eat_food.wav": "pop", "pickup", "coin", "bubble pop"
  - "turn.wav": "beep", "click", "blip", "short beep"
  - "game_over.wav": "game over", "fail", "death", "negative"
  - "button_hover.wav": "hover", "soft click", "ui hover"
  - "button_click.wav": "click", "button", "ui click", "select"
  - "game_start.wav": "start", "begin", "positive", "success"

## 🔧 Audio Specifications

### Background Music
- **Format**: OGG Vorbis (best compression) or MP3
- **Length**: 30 seconds to 2 minutes (will loop automatically)
- **Style**: Ambient, electronic, retro, or chiptune
- **Volume**: Moderate (game auto-adjusts to 30% volume)

### Sound Effects
- **Format**: WAV (fastest loading) or MP3
- **Length**: 0.1 to 1.0 seconds
- **Quality**: 22kHz, 16-bit recommended
- **Volume**: Clear but not overwhelming

## 🎯 Specific Audio Recommendations

### For "eat_food.wav"
- High-pitched pleasant sound (800Hz range)
- Duration: 0.1-0.2 seconds
- Examples: coin pickup, bubble pop, positive beep

### For "turn.wav"
- Quick, subtle sound (400Hz range)
- Duration: 0.05-0.1 seconds
- Examples: soft click, short beep, UI tick

### For "game_over.wav"
- Descending tone or dramatic sound
- Duration: 0.3-0.8 seconds
- Examples: fail sound, descending beep, negative chord

### For Button Sounds
- "button_hover.wav": Very soft, 0.03 seconds
- "button_click.wav": Sharp click, 0.08 seconds

### For "game_start.wav"
- Ascending or positive sound
- Duration: 0.2-0.5 seconds
- Examples: success sound, ascending beep, positive chord

## 🛠️ Audio Conversion Tools

### Free Audio Converters
- **Audacity** - Free, cross-platform audio editor
- **FFmpeg** - Command-line tool for format conversion
- **Online-Convert.com** - Web-based converter
- **VLC Media Player** - Can convert between formats

### Quick Conversion Commands (FFmpeg)
```bash
# Convert MP3 to OGG
ffmpeg -i music.mp3 -c:a libvorbis background_music.ogg

# Convert MP3 to WAV
ffmpeg -i sound.mp3 sound.wav

# Adjust volume (50% in this example)
ffmpeg -i input.wav -filter:a "volume=0.5" output.wav
```

## 🎮 In-Game Audio Controls

- **M Key**: Toggle audio on/off
- **Audio Button**: Click to toggle audio
- **Automatic Volume**: Music at 30%, SFX at 70%
- **Fallback**: Built-in sounds if files missing

## 🔍 Troubleshooting

### Game Runs But No Audio
1. Check if `audio/` folder exists in game directory
2. Verify audio file names match exactly (case-sensitive)
3. Ensure audio files are not corrupted
4. Check console output for error messages

### Audio Files Not Loading
- Supported formats: WAV, OGG, MP3
- File size should be reasonable (< 10MB for music, < 1MB for SFX)
- Avoid special characters in filenames

### Performance Issues
- Use OGG for background music (smaller file size)
- Keep sound effects under 1 second duration
- Lower audio quality if needed (22kHz instead of 44kHz)

## 🎵 Example Audio Search Terms

Copy these search terms into royalty-free audio sites:

**Background Music:**
- "retro game loop"
- "ambient electronic loop"
- "8-bit background music"
- "minimal techno loop"
- "game soundtrack loop"

**Sound Effects:**
- "arcade game sounds"
- "retro game sfx pack"
- "UI sound effects"
- "game pickup sounds"
- "button click sounds"

## 📝 License Notes

When downloading royalty-free audio:
- Check license requirements (some require attribution)
- Ensure commercial use is allowed if distributing
- Keep track of sources for proper crediting
- Consider Creative Commons licensed content

## 🚀 Quick Test

After adding audio files, run the game and:
1. Listen for background music on startup
2. Test button hover/click sounds in menu
3. Play game and listen for turn/eat sounds
4. Trigger game over to hear game over sound
5. Use M key to toggle audio on/off

The game includes built-in placeholder sounds, so it will work even without external audio files!
