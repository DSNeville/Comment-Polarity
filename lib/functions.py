def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(key, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def get_videos(service, **kwargs):
    final_results = []
    results = service.search().list(**kwargs).execute()
 
    i = 0
    max_pages = 3
    while results and i < max_pages:
        final_results.extend(results['items'])
        # Check if another page exists
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.search().list(**kwargs).execute()
            i += 1
        else:
            break
 
    return final_results

def search_videos_by_keyword(service, **kwargs):
    results = get_videos(service, **kwargs)
    final_results = []
    for item in results:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        comments = get_video_comments(service, part='snippet', videoId=video_id, textFormat='plainText')
        final_results.extend([(video_id, title, comment) for comment in comments])
    return final_results

def find_channel_id(service, search_term):
    request = service.channels().list(
    forUsername=search_term,
    part='id,snippet'
    ).execute()
    channel_id = request['items'][0]['id']
    return channel_id

def search_channels(service, search_term):
    request = service.search().list(
        q=search_term,
        part='id,snippet',
        type='channel',
        maxResults='20'
    ).execute()
    
    channel_df = pd.DataFrame(columns=['channel_id','channel'])
    for results in request:
        chan = request['items'][0]['channelTitle']
        c_id = request['items'][0]['channelId']
        channel_df = channel_df.append(pd.Series([chan, c_id],index=channel_df.columns), ignore_index = True)
    
    return channel_df

def get_video_details(service, video_id):
    # takes a video_id and returns the video title, channel, and description

def get_video_comments(service, **kwargs):
    # results = service.commentThreads().list(
    #     part='snippet',
    #     videoId='h2RzmSAZ4Hc',
    #     textFormat='plainText'
    #     ).execute()
    # results
    comment_df = pd.DataFrame(columns=['author','comment','likes'])
    results = service.commentThreads().list(**kwargs).execute()
 
    while results:
        for item in results['items']:
            author = item['snippet']['topLevelComment']['snippet']['authorChannelId']
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            likes = item['snippet']['topLevelComment']['snippet']['likeCount']
            comment_df = comment_df.append(pd.Series([author,comment,likes],index=comment_df.columns), ignore_index = True)
 
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break
 
    return comment_df

def extract_video_description(video):
    try:
        description = video['items'][0]['snippet']['description']
        return description
    except:
        print('No description found')
    
def extract_video_title(video):
    try:
        description = video['items'][0]['snippet']['title']
        return description
    except:
        print('No title found')
        
def get_video_details(service, video_id):
    # takes a video_id and returns the video title, channel, and description
    # video_details = get_video_details(service,'h2RzmSAZ4Hc')
    results = service.videos().list(part='snippet',id=video_id).execute()
    return results