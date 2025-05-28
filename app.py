from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import re
from collections import Counter
import numpy as np

app = Flask(__name__)

def clean_text(text):
    """Nettoie le texte en supprimant les balises HTML et caractères indésirables"""
    if pd.isna(text) or text == '':
        return ""
    
    text = str(text)
    
    # Supprimer les balises HTML complètement
    text = re.sub(r'<br\s*/?>', ' ', text)  # Remplacer <br> par espace
    text = re.sub(r'<[^>]+>', '', text)     # Supprimer toutes les autres balises HTML
    
    # Nettoyer les caractères spéciaux d'encodage
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('%c2%b5', 'µ')  # Caractère µ encodé
    
    # Supprimer les caractères de contrôle et normaliser les espaces
    text = re.sub(r'[^\w\s,.-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def load_and_clean_data():
    """Charge et nettoie les données CSV"""
    try:
        # Charger les données
        df = pd.read_csv('medicament_ma_top5000.csv')
        
        # Supprimer TOUTES les colonnes 'Boite' et 'Boîte' (colonnes dupliquées)
        columns_to_drop = [col for col in df.columns if col.lower() in ['boite', 'boîte']]
        if columns_to_drop:
            df = df.drop(columns_to_drop, axis=1)
            print(f"Colonnes supprimées : {columns_to_drop}")
        
        # Nettoyer le nom des médicaments (supprimer les caractères d'encodage)
        if 'name' in df.columns:
            df['name'] = df['name'].apply(clean_text)
        
        # Nettoyer TOUTES les colonnes textuelles avec des balises HTML
        text_columns = ['Indication(s)', 'Mises en garde', 'Contres-indication(s)', 
                       'Posologies et mode d\'administration', 'Composition',
                       'Distributeur ou fabriquant', 'Classe thérapeutique', 
                       'Dosage', 'Présentation']
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_text)
        
        # Nettoyer les prix (supprimer 'dhs' et convertir en float)
        price_columns = ['PPV', 'Prix hospitalier', 'PPC']
        for col in price_columns:
            if col in df.columns:
                # Convertir en string, supprimer 'dhs' et nettoyer
                df[col] = df[col].astype(str).str.replace(' dhs', '', regex=False)
                df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = df[col].str.replace('nan', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Nettoyer PPV_num avec une attention particulière
        if 'PPV_num' in df.columns:
            df['PPV_num'] = df['PPV_num'].astype(str)
            df['PPV_num'] = df['PPV_num'].str.replace(r'[^\d.,]', '', regex=True)
            df['PPV_num'] = df['PPV_num'].str.replace(',', '.', regex=False)
            df['PPV_num'] = df['PPV_num'].replace(['', 'nan', 'None'], np.nan)
            df['PPV_num'] = pd.to_numeric(df['PPV_num'], errors='coerce')
        
        # Nettoyer Prix Unitaire de la même manière
        if 'Prix Unitaire' in df.columns:
            df['Prix Unitaire'] = df['Prix Unitaire'].astype(str)
            df['Prix Unitaire'] = df['Prix Unitaire'].str.replace(r'[^\d.,]', '', regex=True)
            df['Prix Unitaire'] = df['Prix Unitaire'].str.replace(',', '.', regex=False)
            df['Prix Unitaire'] = df['Prix Unitaire'].replace(['', 'nan', 'None'], np.nan)
            df['Prix Unitaire'] = pd.to_numeric(df['Prix Unitaire'], errors='coerce')
        
        # Remplir les valeurs manquantes des colonnes textuelles seulement
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')
        
        print(f"Données nettoyées avec succès ! Nombre de médicaments : {len(df)}")
        print(f"Colonnes restantes : {list(df.columns)}")
        
        return df
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Charger les données au démarrage
df = load_and_clean_data()

@app.route('/')
def dashboard():
    """Route principale du dashboard"""
    # Statistiques générales
    total_medicaments = len(df)
    
    # Calculer la moyenne des prix en excluant les valeurs NaN
    if 'PPV_num' in df.columns and not df['PPV_num'].empty:
        prix_valides = df['PPV_num'].dropna()
        moyenne_prix = prix_valides.mean() if len(prix_valides) > 0 else 0
    else:
        moyenne_prix = 0
    
    nb_distributeurs = df['Distributeur ou fabriquant'].nunique() if 'Distributeur ou fabriquant' in df.columns else 0
    nb_classes = df['Classe thérapeutique'].nunique() if 'Classe thérapeutique' in df.columns else 0
    
    stats = {
        'total_medicaments': total_medicaments,
        'moyenne_prix': round(moyenne_prix, 2) if not pd.isna(moyenne_prix) else 0,
        'nb_distributeurs': nb_distributeurs,
        'nb_classes': nb_classes
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/api/classe-therapeutique')
def classe_therapeutique():
    """API pour la répartition par classe thérapeutique"""
    if 'Classe thérapeutique' not in df.columns:
        return jsonify({'error': 'Colonne Classe thérapeutique non trouvée'})
    
    # Compter les médicaments par classe thérapeutique
    classe_counts = df['Classe thérapeutique'].value_counts().head(10)
    
    # Créer un graphique en barres horizontales moderne
    fig = go.Figure(data=[
        go.Bar(
            y=classe_counts.index,
            x=classe_counts.values,
            orientation='h',
            marker=dict(
                color=classe_counts.values,
                colorscale='Viridis',
                showscale=False,
                line=dict(width=0)
            ),
            text=classe_counts.values,
            texttemplate='<b>%{text}</b>',
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Médicaments: <b>%{x}</b><extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="🏥 Top 10 des Classes Thérapeutiques",
            x=0.5,
            font=dict(size=20, color="#2c3e50", family="Segoe UI")
        ),
        xaxis=dict(
            title="Nombre de Médicaments",
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color="#34495e")
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11, color="#34495e"),
            automargin=True
        ),
        plot_bgcolor='rgba(248,249,250,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=10, r=30, t=80, b=40),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#2c3e50")
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/distribution-prix')
def distribution_prix():
    """API pour la distribution des prix"""
    if 'PPV_num' not in df.columns:
        return jsonify({'error': 'Colonne PPV_num non trouvée'})
    
    # Filtrer les prix valides
    prix_valides = df[df['PPV_num'] > 0]['PPV_num']
    
    # Créer un histogramme moderne avec dégradé
    fig = go.Figure(data=[
        go.Histogram(
            x=prix_valides,
            nbinsx=30,
            marker=dict(
                color=prix_valides,
                colorscale='plasma',
                opacity=0.8,
                line=dict(width=0.5, color='white')
            ),
            hovertemplate='Prix: %{x:.2f} DHS<br>Fréquence: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="💰 Distribution des Prix des Médicaments",
            x=0.5,
            font=dict(size=20, color="#2c3e50", family="Segoe UI")
        ),
        xaxis=dict(
            title="Prix (DHS)",
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color="#34495e")
        ),
        yaxis=dict(
            title="Nombre de Médicaments",
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color="#34495e")
        ),
        plot_bgcolor='rgba(248,249,250,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=60, r=30, t=80, b=60),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#2c3e50")
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/top-distributeurs')
def top_distributeurs():
    """API pour les top distributeurs"""
    if 'Distributeur ou fabriquant' not in df.columns:
        return jsonify({'error': 'Colonne Distributeur non trouvée'})
    
    # Compter les médicaments par distributeur
    dist_counts = df['Distributeur ou fabriquant'].value_counts().head(8)
    
    # Couleurs modernes pour le graphique circulaire
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=dist_counts.index,
            values=dist_counts.values,
            hole=0.4,  # Donut chart
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=11, color="#2c3e50"),
            hovertemplate='<b>%{label}</b><br>Médicaments: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="🏭 Top 8 des Distributeurs/Fabricants",
            x=0.5,
            font=dict(size=20, color="#2c3e50", family="Segoe UI")
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=20, r=20, t=80, b=40),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#2c3e50"),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/formes-medicaments')
def formes_medicaments():
    """API pour les formes de médicaments"""
    if 'Forme' not in df.columns:
        return jsonify({'error': 'Colonne Forme non trouvée'})
    
    # Compter les différentes formes
    forme_counts = df['Forme'].value_counts().head(10)
    
    # Créer un graphique en barres avec animation et couleurs dégradées
    fig = go.Figure(data=[
        go.Bar(
            y=forme_counts.index,
            x=forme_counts.values,
            orientation='h',
            marker=dict(
                color=forme_counts.values,
                colorscale='Turbo',
                showscale=False,
                line=dict(width=0)
            ),
            text=forme_counts.values,
            texttemplate='<b>%{text}</b>',
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Médicaments: <b>%{x}</b><extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="💊 Répartition par Forme de Médicament",
            x=0.5,
            font=dict(size=20, color="#2c3e50", family="Segoe UI")
        ),
        xaxis=dict(
            title="Nombre de Médicaments",
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color="#34495e")
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11, color="#34495e"),
            automargin=True
        ),
        plot_bgcolor='rgba(248,249,250,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=10, r=30, t=80, b=40),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#2c3e50")
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/prix-comparaison')
def prix_comparaison():
    """API pour comparer les prix PPV et hospitalier"""
    if 'PPV_num' not in df.columns or 'Prix hospitalier' not in df.columns:
        return jsonify({'error': 'Colonnes de prix non trouvées'})
    
    # Filtrer les données avec les deux prix disponibles
    df_prix = df[(df['PPV_num'] > 0) & (df['Prix hospitalier'] > 0)].head(15)
    
    fig = go.Figure()
    
    # Prix Public (PPV)
    fig.add_trace(go.Scatter(
        x=df_prix['name'],
        y=df_prix['PPV_num'],
        mode='markers+lines',
        name='Prix Public (PPV)',
        marker=dict(
            color='#667eea',
            size=10,
            line=dict(width=2, color='white')
        ),
        line=dict(color='#667eea', width=3),
        hovertemplate='<b>%{x}</b><br>PPV: %{y:.2f} DHS<extra></extra>'
    ))
    
    # Prix Hospitalier
    fig.add_trace(go.Scatter(
        x=df_prix['name'],
        y=df_prix['Prix hospitalier'],
        mode='markers+lines',
        name='Prix Hospitalier',
        marker=dict(
            color='#f5576c',
            size=10,
            line=dict(width=2, color='white')
        ),
        line=dict(color='#f5576c', width=3),
        hovertemplate='<b>%{x}</b><br>Prix Hospitalier: %{y:.2f} DHS<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="📊 Comparaison Prix Public vs Prix Hospitalier",
            x=0.5,
            font=dict(size=20, color="#2c3e50", family="Segoe UI")
        ),
        xaxis=dict(
            title="Médicaments",
            tickangle=-45,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=10, color="#34495e")
        ),
        yaxis=dict(
            title="Prix (DHS)",
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color="#34495e")
        ),
        plot_bgcolor='rgba(248,249,250,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=60, r=30, t=80, b=120),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#2c3e50"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/search')
def search():
    """API pour rechercher des médicaments"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    # Recherche dans le nom et la composition
    results = df[
        df['name'].str.lower().str.contains(query, na=False) |
        df['Composition'].str.lower().str.contains(query, na=False)
    ].head(10)
    
    return jsonify(results[['name', 'Composition', 'PPV_num', 'Classe thérapeutique']].to_dict('records'))

@app.route('/api/substances-psychoactives')
def substances_psychoactives():
    """API pour les substances psychoactives"""
    if 'Substance (s) psychoactive (s)' not in df.columns:
        return jsonify({'error': 'Colonne substances psychoactives non trouvée'})
    
    # Compter les substances psychoactives
    psycho_counts = df['Substance (s) psychoactive (s)'].value_counts()
    
    # Couleurs modernes pour le graphique circulaire
    colors = ['#43e97b', '#f5576c', '#4facfe', '#38f9d7', '#667eea']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=psycho_counts.index,
            values=psycho_counts.values,
            hole=0.3,  # Donut chart
            marker=dict(
                colors=colors[:len(psycho_counts)],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textposition='auto',
            textfont=dict(size=12, color="white", family="Segoe UI"),
            hovertemplate='<b>%{label}</b><br>Médicaments: %{value}<br>Pourcentage: %{percent}<extra></extra>',
            pull=[0.1 if i == 0 else 0 for i in range(len(psycho_counts))]  # Mettre en évidence le premier segment
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="🧠 Répartition des Substances Psychoactives",
            x=0.5,
            font=dict(size=20, color="#2c3e50", family="Segoe UI")
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=20, r=20, t=80, b=40),
        font=dict(family="Segoe UI, Arial, sans-serif", color="#2c3e50"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/data')
def data_view():
    """Page d'affichage des données nettoyées"""
    # Préparer un échantillon des données pour l'affichage
    sample_df = df.head(50)  # Afficher les 50 premiers médicaments
    
    # Sélectionner les colonnes pertinentes pour l'affichage
    columns_to_show = ['name', 'Indication(s)', 'Mises en garde', 'Contres-indication(s)', 
                       'Posologies et mode d\'administration', 'Composition',
                       'Distributeur ou fabriquant', 'Classe thérapeutique', 
                       'Dosage', 'Présentation', 'PPV', 'Prix hospitalier', 'PPC',
                       'PPV_num', 'Prix Unitaire']
    
    # Filtrer les colonnes existantes
    columns_to_show = [col for col in columns_to_show if col in df.columns]
    
    # Créer une table HTML avec les données échantillonnées
    table_html = sample_df.to_html(classes='table table-striped table-hover', index=False, columns=columns_to_show)
    
    return render_template('data_view.html', table=table_html)

if __name__ == '__main__':
    app.run(debug=True)