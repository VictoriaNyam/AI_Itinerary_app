import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from app import db
from app.models import POI, Itinerary  # Added Itinerary import
from flask_login import current_user  # Added current_user import
from math import radians, cos, sin, sqrt, atan2

# Configuration: fixed clusters and POI limit per cluster
def load_poi_data():
    df = pd.read_csv('dataset/London_cleaned_with_all_pois.csv')
    df = df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    df['Original_Latitude'] = df['Latitude']
    df['Original_Longitude'] = df['Longitude']
    df = normalize_coordinates(df)
    df = normalize_activity_features(df, ACTIVITY_COLS)
    return df

# Constants
K_CLUSTERS = 10          # number of clusters for KMeans
POIS_PER_CLUSTER = 5     # number of POIs to select per cluster

# All possible activity columns
ACTIVITY_COLS = [
    'nature', 'nightlife', 'drink', 'music', 'dance', 'history',
    'sports', 'art', 'museum', 'walk', 'restaurant', 'movie'
]

# Normalize latitude/longitude to [0,1]
def normalize_coordinates(df):
    scaler = MinMaxScaler()
    df[['Norm_Latitude', 'Norm_Longitude']] = scaler.fit_transform(
        df[['Latitude', 'Longitude']]
    )
    return df

# Normalize activity binary flags to [0,1]
def normalize_activity_features(df, activity_cols):
    scaler = MinMaxScaler()
    df[activity_cols] = scaler.fit_transform(df[activity_cols])
    return df

# Filter POIs by selected activities
def filter_pois_by_activity(df, selected_activities):
    return df[df[selected_activities].sum(axis=1) > 0].reset_index(drop=True)

# Apply KMeans clustering on geo + activity features
# days: used later for itinerary split; clusters fixed at K_CLUSTERS
# selected_activities: list of columns, default all
def apply_kmeans(df, days, selected_activities=None):
    if selected_activities is None:
        selected_activities = ACTIVITY_COLS
    feature_cols = ['Norm_Latitude', 'Norm_Longitude'] + selected_activities
    X = df[feature_cols].values

    kmeans = KMeans(n_clusters=K_CLUSTERS, random_state=42)
    labels = kmeans.fit_predict(X)
    df['cluster'] = labels

    # Silhouette Score
    if len(set(labels)) > 1 and len(labels) > K_CLUSTERS:
        score = silhouette_score(X, labels)
        print(f"Silhouette Score for k={K_CLUSTERS}: {score:.4f}")
    else:
        print("Silhouette Score cannot be computed (>=2 clusters and more samples than clusters).")

    return df, kmeans

# Select top POIs per cluster in mixed feature space
def select_representative_pois(df, kmeans, pois_per_cluster=POIS_PER_CLUSTER):
    reps = []
    for idx, center in enumerate(kmeans.cluster_centers_):
        cluster_df = df[df['cluster'] == idx].copy()
        if cluster_df.empty:
            continue
        diffs = cluster_df[['Norm_Latitude', 'Norm_Longitude'] + ACTIVITY_COLS] - center
        cluster_df['feat_dist'] = (diffs ** 2).sum(axis=1)
        chosen = cluster_df.nsmallest(pois_per_cluster, 'feat_dist')
        reps.extend(chosen.to_dict(orient='records'))
    return reps

# Split list into n approx equal parts
def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [
        lst[i*k + min(i, m):(i+1)*k + min(i+1, m)]
        for i in range(n)
    ]

# Haversine distance between two POI dicts
def calculate_haversine_distance(p1, p2):
    lat1, lon1 = radians(p1['latitude']), radians(p1['longitude'])
    lat2, lon2 = radians(p2['latitude']), radians(p2['longitude'])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return 6371 * c

# Total travel distance of an itinerary list
def calculate_total_distance(itin):
    return sum(
        calculate_haversine_distance(itin[i], itin[i+1])
        for i in range(len(itin) - 1)
    )

# 2-opt local search to minimize travel distance
def opt2(itin):
    improved = True
    while improved:
        improved = False
        best = calculate_total_distance(itin)
        for i in range(1, len(itin)-1):
            for j in range(i+1, len(itin)):
                new_itin = itin[:i] + itin[i:j+1][::-1] + itin[j+1:]
                dist = calculate_total_distance(new_itin)
                if dist < best:
                    itin, best, improved = new_itin, dist, True
                    break
            if improved:
                break
    return itin

# Build and save final daily itineraries
def generate_itineraries(representative_pois, selected_activities, days):
    # Deduplicate and prioritize by activity match
    unique = {poi['name']: poi for poi in representative_pois}.values()
    sorted_pois = sorted(
        unique,
        key=lambda p: sum(p.get(act, 0) for act in selected_activities),
        reverse=True
    )
    # Limit total displayed
    max_pois = days * POIS_PER_CLUSTER
    sorted_pois = sorted_pois[:max_pois]

    # Split into days
    daily_groups = split_list(list(sorted_pois), days)
    final = []
    for day_num, group in enumerate(daily_groups, start=1):
        entries = []
        for p in group:
            entry = {
                'name': p['name'],
                'latitude': p['Original_Latitude'],
                'longitude': p['Original_Longitude'],
                'address': p.get('address', ''),
                'day': day_num
            }
            entry.update({act: p.get(act, 0) for act in selected_activities})
            entries.append(entry)
        before = calculate_total_distance(entries)
        optimized = opt2(entries)
        after = calculate_total_distance(optimized)
        print(f"Day {day_num}: before {before:.2f} km, after {after:.2f} km, improvement {before-after:.2f} km")
        final.append(optimized)

    # Persist to DB using relationships
    for day_index, itin_list in enumerate(final, start=1):
        itin = Itinerary(
            user_id=current_user.id,
            name=f"Itinerary Day {day_index}"
        )
        for poi in itin_list:
            poi_obj = POI(
                name=poi['name'],
                address=poi['address'],
                latitude=poi['latitude'],
                longitude=poi['longitude'],
                original_latitude=poi['latitude'],
                original_longitude=poi['longitude'],
                day=poi['day']
            )
            itin.pois.append(poi_obj)
        db.session.add(itin)
    db.session.commit()
    return final
