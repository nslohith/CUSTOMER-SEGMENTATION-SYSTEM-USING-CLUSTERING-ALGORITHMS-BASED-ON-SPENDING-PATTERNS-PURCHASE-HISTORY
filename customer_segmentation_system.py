"""
Customer Segmentation System using Clustering Algorithms
Segments customers based on spending patterns, purchase history, and demographics
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def generate_customer_dataset(n_customers=2000, random_state=42):
    """Generate synthetic customer dataset"""
    np.random.seed(random_state)
    
    data = []
    
    for i in range(n_customers):
        # Demographics
        age = np.random.randint(18, 75)
        gender = np.random.choice(['Male', 'Female', 'Other'], p=[0.45, 0.50, 0.05])
        location = np.random.choice(['Urban', 'Suburban', 'Rural'], p=[0.50, 0.35, 0.15])
        
        # Purchase behavior
        purchase_frequency = np.random.poisson(lam=8) + 1
        avg_transaction_value = np.random.lognormal(mean=4.5, sigma=1.2)
        total_spending = purchase_frequency * avg_transaction_value
        
        # Product preferences
        product_category = np.random.choice(['Electronics', 'Fashion', 'Home', 'Beauty', 'Sports'], 
                                           p=[0.25, 0.30, 0.20, 0.15, 0.10])
        loyalty_score = np.random.uniform(0, 100)
        
        # Customer tenure
        tenure_months = np.random.randint(1, 60)
        
        # Online vs offline preference
        online_preference = np.random.uniform(0, 100)
        
        data.append({
            'Customer_ID': f'C{i:05d}',
            'Age': age,
            'Gender': gender,
            'Location': location,
            'Purchase_Frequency': purchase_frequency,
            'Avg_Transaction_Value': round(avg_transaction_value, 2),
            'Total_Spending': round(total_spending, 2),
            'Product_Category': product_category,
            'Loyalty_Score': round(loyalty_score, 2),
            'Tenure_Months': tenure_months,
            'Online_Preference': round(online_preference, 2)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('/home/ubuntu/customer_segmentation_data.csv', index=False)
    print(f"Generated customer dataset: {len(df)} records")
    return df

def prepare_features(df):
    """Prepare features for clustering"""
    df_processed = df.copy()
    
    # Encode categorical variables
    le_gender = LabelEncoder()
    le_location = LabelEncoder()
    le_category = LabelEncoder()
    
    df_processed['Gender_Encoded'] = le_gender.fit_transform(df_processed['Gender'])
    df_processed['Location_Encoded'] = le_location.fit_transform(df_processed['Location'])
    df_processed['Category_Encoded'] = le_category.fit_transform(df_processed['Product_Category'])
    
    # Select features for clustering
    features = ['Age', 'Purchase_Frequency', 'Avg_Transaction_Value', 'Total_Spending',
                'Loyalty_Score', 'Tenure_Months', 'Online_Preference', 'Gender_Encoded',
                'Location_Encoded', 'Category_Encoded']
    
    X = df_processed[features].copy()
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, features, df_processed

def find_optimal_k(X_scaled, max_k=10):
    """Find optimal number of clusters using elbow method"""
    inertias = []
    silhouette_scores = []
    K_range = range(2, max_k + 1)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    
    return list(K_range), inertias, silhouette_scores

def train_clustering_models(X_scaled, df):
    """Train multiple clustering models"""
    results = []
    
    # K-Means with optimal k
    kmeans_3 = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans_3_labels = kmeans_3.fit_predict(X_scaled)
    
    kmeans_4 = KMeans(n_clusters=4, random_state=42, n_init=10)
    kmeans_4_labels = kmeans_4.fit_predict(X_scaled)
    
    kmeans_5 = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans_5_labels = kmeans_5.fit_predict(X_scaled)
    
    # DBSCAN
    dbscan = DBSCAN(eps=1.5, min_samples=10)
    dbscan_labels = dbscan.fit_predict(X_scaled)
    
    # Calculate metrics
    models = [
        ('K-Means (k=3)', kmeans_3_labels, kmeans_3.inertia_),
        ('K-Means (k=4)', kmeans_4_labels, kmeans_4.inertia_),
        ('K-Means (k=5)', kmeans_5_labels, kmeans_5.inertia_),
        ('DBSCAN', dbscan_labels, None)
    ]
    
    for model_name, labels, inertia in models:
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        if n_clusters > 1:
            silhouette = silhouette_score(X_scaled, labels)
            davies_bouldin = davies_bouldin_score(X_scaled, labels)
        else:
            silhouette = -1
            davies_bouldin = -1
        
        results.append({
            'Model': model_name,
            'Num_Clusters': n_clusters,
            'Silhouette_Score': round(silhouette, 4),
            'Davies_Bouldin_Score': round(davies_bouldin, 4),
            'Labels': labels
        })
    
    results_df = pd.DataFrame(results)
    results_df.to_csv('/home/ubuntu/clustering_model_results.csv', index=False)
    
    return results_df, results

def analyze_clusters(df, labels, model_name):
    """Analyze cluster characteristics"""
    df_clustered = df.copy()
    df_clustered['Cluster'] = labels
    
    analysis = []
    
    for cluster in sorted(df_clustered['Cluster'].unique()):
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster]
        
        analysis.append({
            'Model': model_name,
            'Cluster': cluster,
            'Size': len(cluster_data),
            'Avg_Age': round(cluster_data['Age'].mean(), 2),
            'Avg_Purchase_Freq': round(cluster_data['Purchase_Frequency'].mean(), 2),
            'Avg_Spending': round(cluster_data['Total_Spending'].mean(), 2),
            'Avg_Loyalty': round(cluster_data['Loyalty_Score'].mean(), 2),
            'Avg_Tenure': round(cluster_data['Tenure_Months'].mean(), 2)
        })
    
    return pd.DataFrame(analysis)

def generate_visualizations(df, X_scaled, results):
    """Generate comprehensive visualizations"""
    
    # 1. Elbow Method and Silhouette Scores
    K_range, inertias, silhouette_scores = find_optimal_k(X_scaled)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Number of Clusters (k)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Inertia', fontsize=11, fontweight='bold')
    axes[0].set_title('Elbow Method for Optimal k', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(K_range, silhouette_scores, 'go-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Number of Clusters (k)', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Silhouette Score', fontsize=11, fontweight='bold')
    axes[1].set_title('Silhouette Score vs k', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/clustering_optimization.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: clustering_optimization.png")
    
    # 2. Model Comparison
    model_names = results['Model'].tolist()
    silhouette_scores_models = results['Silhouette_Score'].tolist()
    davies_bouldin_scores = results['Davies_Bouldin_Score'].tolist()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].barh(model_names, silhouette_scores_models, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    axes[0].set_xlabel('Silhouette Score', fontsize=11, fontweight='bold')
    axes[0].set_title('Model Comparison: Silhouette Score', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    axes[1].barh(model_names, davies_bouldin_scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    axes[1].set_xlabel('Davies-Bouldin Score (Lower is Better)', fontsize=11, fontweight='bold')
    axes[1].set_title('Model Comparison: Davies-Bouldin Score', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/clustering_model_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: clustering_model_comparison.png")
    
    # 3. Cluster Distribution (K-Means k=4)
    best_result = results[results['Model'] == 'K-Means (k=4)'].iloc[0]
    labels = best_result['Labels']
    
    df_clustered = df.copy()
    df_clustered['Cluster'] = labels
    
    cluster_counts = df_clustered['Cluster'].value_counts().sort_index()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Cluster distribution
    axes[0, 0].bar(cluster_counts.index, cluster_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    axes[0, 0].set_xlabel('Cluster', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Number of Customers', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Cluster Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # Average spending by cluster
    avg_spending = df_clustered.groupby('Cluster')['Total_Spending'].mean()
    axes[0, 1].bar(avg_spending.index, avg_spending.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    axes[0, 1].set_xlabel('Cluster', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Average Spending ($)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Average Spending by Cluster', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Average loyalty by cluster
    avg_loyalty = df_clustered.groupby('Cluster')['Loyalty_Score'].mean()
    axes[1, 0].bar(avg_loyalty.index, avg_loyalty.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    axes[1, 0].set_xlabel('Cluster', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Average Loyalty Score', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Average Loyalty by Cluster', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Average tenure by cluster
    avg_tenure = df_clustered.groupby('Cluster')['Tenure_Months'].mean()
    axes[1, 1].bar(avg_tenure.index, avg_tenure.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    axes[1, 1].set_xlabel('Cluster', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Average Tenure (Months)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Average Tenure by Cluster', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/clustering_cluster_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: clustering_cluster_analysis.png")
    
    # 4. Customer Demographics by Cluster
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Age distribution
    for cluster in sorted(df_clustered['Cluster'].unique()):
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster]
        axes[0, 0].hist(cluster_data['Age'], alpha=0.6, label=f'Cluster {cluster}', bins=15)
    axes[0, 0].set_xlabel('Age', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Age Distribution by Cluster', fontsize=12, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Purchase frequency distribution
    for cluster in sorted(df_clustered['Cluster'].unique()):
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster]
        axes[0, 1].hist(cluster_data['Purchase_Frequency'], alpha=0.6, label=f'Cluster {cluster}', bins=15)
    axes[0, 1].set_xlabel('Purchase Frequency', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Purchase Frequency Distribution', fontsize=12, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Spending distribution
    for cluster in sorted(df_clustered['Cluster'].unique()):
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster]
        axes[1, 0].hist(cluster_data['Total_Spending'], alpha=0.6, label=f'Cluster {cluster}', bins=15)
    axes[1, 0].set_xlabel('Total Spending ($)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Spending Distribution by Cluster', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Online preference distribution
    for cluster in sorted(df_clustered['Cluster'].unique()):
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster]
        axes[1, 1].hist(cluster_data['Online_Preference'], alpha=0.6, label=f'Cluster {cluster}', bins=15)
    axes[1, 1].set_xlabel('Online Preference (%)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Online Preference Distribution', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/clustering_demographics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: clustering_demographics.png")
    
    # 5. Cluster Profiles Heatmap
    cluster_profiles = df_clustered.groupby('Cluster')[['Age', 'Purchase_Frequency', 'Total_Spending', 
                                                         'Loyalty_Score', 'Tenure_Months', 'Online_Preference']].mean()
    
    # Normalize for heatmap
    cluster_profiles_normalized = (cluster_profiles - cluster_profiles.min()) / (cluster_profiles.max() - cluster_profiles.min())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(cluster_profiles_normalized.T, annot=True, fmt='.2f', cmap='YlOrRd', 
                cbar_kws={'label': 'Normalized Score'}, ax=ax, linewidths=0.5)
    ax.set_xlabel('Cluster', fontsize=11, fontweight='bold')
    ax.set_ylabel('Features', fontsize=11, fontweight='bold')
    ax.set_title('Cluster Profiles Heatmap (Normalized)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/clustering_profiles_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: clustering_profiles_heatmap.png")

def main():
    print("="*80)
    print("CUSTOMER SEGMENTATION SYSTEM")
    print("="*80)
    
    print("\n[1] Generating customer dataset...")
    df = generate_customer_dataset(n_customers=2000)
    
    print("\n[2] Preparing features...")
    X_scaled, features, df_processed = prepare_features(df)
    print(f"Features used: {features}")
    
    print("\n[3] Training clustering models...")
    results_df, results = train_clustering_models(X_scaled, df)
    print("\nModel Results:")
    print(results_df.to_string())
    
    print("\n[4] Analyzing clusters...")
    best_model = [r for r in results if r['Model'] == 'K-Means (k=4)'][0]
    cluster_analysis = analyze_clusters(df, best_model['Labels'], 'K-Means (k=4)')
    cluster_analysis.to_csv('/home/ubuntu/cluster_characteristics.csv', index=False)
    print("\nCluster Characteristics:")
    print(cluster_analysis.to_string())
    
    print("\n[5] Generating visualizations...")
    generate_visualizations(df, X_scaled, results_df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All files generated successfully")
    print("="*80)

if __name__ == "__main__":
    main()
