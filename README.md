# Activity Tracker MVP

A Streamlit web application for real-time and historical activity logging with Supabase backend.

## Features

- ⏱️ **Real-time activity logging** with built-in timer
- 📍 **Location tracking** (GPS + manual fallback)
- 🎯 **Perception scoring** (-5 to +5 scale)
- 🏷️ **Tag system** for categorization
- 📸 **Media uploads** (images and videos)
- 📊 **Dashboard** with statistics and recent activities
- 📅 **Historical entries** with custom date/time
- 🔐 **Simple authentication** (admin/password)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Supabase

1. Create a new Supabase project at https://supabase.com
2. Create the activities table with this SQL:

```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    timestamp TIMESTAMPTZ NOT NULL,
    type TEXT CHECK (type IN ('live', 'historical')),
    location JSONB,
    perception_score INTEGER CHECK (perception_score BETWEEN -5 AND 5),
    tags TEXT[],
    description TEXT,
    timer_duration INTEGER,
    media_urls TEXT[]
);

-- Enable Row Level Security
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed)
CREATE POLICY "Allow all operations" ON activities
    FOR ALL USING (true);
```

3. Create a storage bucket for media files:
   - Go to Storage in your Supabase dashboard
   - Create a new bucket named "activity-media"
   - Make it public if you want public access to media files

### 3. Environment Configuration

1. Copy `.env.template` to `.env`
2. Update the values with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4. Run the Application

```bash
streamlit run app.py
```

## Usage

### Authentication
- Username: `admin`
- Password: `password`

### Pages

1. **Dashboard** - View recent activities and statistics
2. **Live Update** - Track activities in real-time with timer
3. **Historical Entry** - Add past activities with custom dates

### Features Guide

- **Timer**: Start/stop timer for accurate duration tracking
- **Location**: Use GPS button or manual entry
- **Perception Score**: Rate activities from -5 (very negative) to +5 (very positive)
- **Tags**: Comma-separated tags for categorization
- **Media**: Upload images (JPG, PNG) and videos (MP4, MOV)

## File Structure

```
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables
├── .env.template            # Environment template
├── pages/
│   ├── 1_Dashboard.py       # Dashboard with stats and recent activities
│   ├── 2_Live_Update.py     # Real-time logging with timer
│   └── 3_Historical.py      # Historical activity entry
└── utils/
    ├── supabase_client.py   # Supabase connection
    ├── data_handler.py      # Database CRUD operations
    ├── location.py          # GPS and manual location capture
    └── auth.py              # Simple authentication
```

## Database Schema

The `activities` table stores:
- `id`: Unique identifier (UUID)
- `created_at`: When record was created
- `timestamp`: When activity occurred
- `type`: 'live' or 'historical'
- `location`: JSON with lat, lng, description
- `perception_score`: Integer from -5 to 5
- `tags`: Array of strings
- `description`: Text description
- `timer_duration`: Duration in seconds (null for historical)
- `media_urls`: Array of media file URLs

## Deployment

The app can be deployed to:
- **Streamlit Community Cloud**
- **Heroku**
- **Railway**
- **Any platform supporting Streamlit**

Make sure to set environment variables in your deployment platform.

## Troubleshooting

1. **Connection Issues**: Check your Supabase URL and API key
2. **Permission Errors**: Verify RLS policies in Supabase
3. **Media Upload Fails**: Check storage bucket permissions
4. **GPS Not Working**: Use manual location entry as fallback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use and modify as needed.