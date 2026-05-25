# Last.fm API Setup

The WAV-to-FLAC converter can use Last.fm as an optional metadata source after MusicBrainz and AcoustID. It is useful for artist normalization, genre hints, and metadata lookup for tracks that are hard to identify from MusicBrainz alone.

## Get API Credentials

1. Sign in or create an account at `https://www.last.fm`.
2. Open `https://www.last.fm/api`.
3. Choose "Get an API account".
4. Use a name such as `Media Converter Organizer`.
5. Keep the generated API key. The shared secret is optional for the current read-only lookup path.

## Configure The App

Create a `.env` file in the project root:

```env
LASTFM_API_KEY=your_lastfm_api_key_here
LASTFM_API_SECRET=your_lastfm_secret_here
```

The app loads `.env` through `python-dotenv` when it is installed. Environment variables also work:

```cmd
set LASTFM_API_KEY=your_lastfm_api_key_here
set LASTFM_API_SECRET=your_lastfm_secret_here
```

```bash
export LASTFM_API_KEY=your_lastfm_api_key_here
export LASTFM_API_SECRET=your_lastfm_secret_here
```

## Test From The Command Line

Run from the project root:

```bash
python src/wav_to_flac_converter.py "path\to\wav_folder" --fingerprinting
```

Look for one of these log messages:

```text
[LASTFM] Last.fm API enabled
[LASTFM] Last.fm API key not configured
```

## Metadata Lookup Order

The converter prefers existing trustworthy metadata, then tries progressively broader lookup methods:

1. Existing FLAC metadata.
2. MusicBrainz album lookup.
3. MusicBrainz recording lookup.
4. AcoustID fingerprint lookup when `--fingerprinting` is enabled and `fpcalc` is available.
5. Last.fm text search when `LASTFM_API_KEY` is configured.
6. Directory and filename fallback.

## Troubleshooting

### Last.fm API Key Not Configured

- Confirm `.env` is in the project root.
- Confirm the variable name is exactly `LASTFM_API_KEY`.
- Restart the app or terminal after changing environment variables.

### Invalid API Key

- Copy the full key from the Last.fm API page again.
- Remove surrounding quotes or trailing spaces from `.env`.
- Confirm the key is not the application shared secret.

### Track Not Found

This is normal for rare tracks. The converter will continue through the fallback strategy and use MusicBrainz, AcoustID, or directory-derived metadata when available.

### Fingerprinting Does Not Run

Last.fm lookup does not require `fpcalc`, but AcoustID fingerprinting does. Confirm:

```bash
fpcalc -version
```
