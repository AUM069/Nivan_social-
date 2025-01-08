import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json


def generate_large_instagram_dataset(num_posts=500):

    np.random.seed(42)


    post_types = ['carousel', 'reels', 'static_image']
    post_type_weights = [0.35, 0.45, 0.20]


    time_slots = ['morning', 'afternoon', 'evening', 'night']
    time_weights = [0.3, 0.25, 0.35, 0.1]

    # Generate base data
    data = {
        'post_id': list(range(1, num_posts + 1)),
        'post_type': list(np.random.choice(post_types, size=num_posts, p=post_type_weights)),
        'time_of_day': list(np.random.choice(time_slots, size=num_posts, p=time_weights)),
        'posted_date': [(datetime.now() - timedelta(days=x % 180)).strftime('%Y-%m-%d')
                        for x in range(num_posts)],
    }


    likes = []
    comments = []
    shares = []
    saves = []
    reach = []
    views = []

    for idx, (post_type, time_slot) in enumerate(zip(data['post_type'], data['time_of_day'])):

        time_multiplier = {
            'morning': 0.9,
            'afternoon': 1.0,
            'evening': 1.2,
            'night': 0.7
        }[time_slot]


        day_of_week = (datetime.strptime(data['posted_date'][idx], '%Y-%m-%d').weekday())
        weekend_multiplier = 1.3 if day_of_week >= 5 else 1.0


        if post_type == 'reels':
            base_likes = np.random.lognormal(7, 0.5)
            likes.append(int(base_likes * time_multiplier * weekend_multiplier))
            comments.append(int(base_likes * 0.08 * time_multiplier * weekend_multiplier))
            shares.append(int(base_likes * 0.15 * time_multiplier * weekend_multiplier))
            saves.append(int(base_likes * 0.05 * time_multiplier * weekend_multiplier))
            reach.append(int(base_likes * 2.5 * time_multiplier * weekend_multiplier))
            views.append(int(base_likes * 3.5 * time_multiplier * weekend_multiplier))
        elif post_type == 'carousel':
            base_likes = np.random.lognormal(6.5, 0.4)
            likes.append(int(base_likes * time_multiplier * weekend_multiplier))
            comments.append(int(base_likes * 0.06 * time_multiplier * weekend_multiplier))
            shares.append(int(base_likes * 0.10 * time_multiplier * weekend_multiplier))
            saves.append(int(base_likes * 0.08 * time_multiplier * weekend_multiplier))
            reach.append(int(base_likes * 2.2 * time_multiplier * weekend_multiplier))
            views.append(0)
        else:
            base_likes = np.random.lognormal(6, 0.3)
            likes.append(int(base_likes * time_multiplier * weekend_multiplier))
            comments.append(int(base_likes * 0.05 * time_multiplier * weekend_multiplier))
            shares.append(int(base_likes * 0.08 * time_multiplier * weekend_multiplier))
            saves.append(int(base_likes * 0.04 * time_multiplier * weekend_multiplier))
            reach.append(int(base_likes * 2.0 * time_multiplier * weekend_multiplier))
            views.append(0)


    data['likes'] = likes
    data['comments'] = comments
    data['shares'] = shares
    data['saves'] = saves
    data['reach'] = reach
    data['views'] = views


    data['engagement_rate'] = [round(((l + c + s + sv) / r) * 100, 2)
                               for l, c, s, sv, r in zip(likes, comments, shares, saves, reach)]


    data['hashtag_count'] = np.random.randint(5, 31, size=num_posts)


    data['posting_consistency'] = np.random.randint(1, 11, size=num_posts)


    df = pd.DataFrame(data)


    df = df.sort_values('posted_date', ascending=False)

    return df


def save_to_json(df, filename='large_instagram_engagement_data.json'):

    records = df.to_dict('records')


    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

    print(f"Dataset saved to {filename}")



instagram_df = generate_large_instagram_dataset()


save_to_json(instagram_df)


print("\nDataset Summary:")
print(f"Total number of posts: {len(instagram_df)}")
print("\nPost type distribution:")
print(instagram_df['post_type'].value_counts(normalize=True).round(3) * 100)

print("\nEngagement Statistics:")
print(instagram_df[['likes', 'comments', 'shares', 'saves', 'reach', 'engagement_rate']].describe().round(2))


print("\nSample of first few records:")
print(instagram_df.head().to_dict('records'))
