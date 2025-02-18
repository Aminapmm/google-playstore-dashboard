import streamlit as st
import pandas as pd
from app import url_object
from sqlalchemy import create_engine,text
import plotly.express as px
from streamlit_extras.switch_page_button import switch_page
import plotly.graph_objects as go
import time

def load_data(query):

    engine = create_engine(url_object)

    with engine.connect() as conn:
        #First Set index 
        sql_create_index = text("CREATE INDEX IF NOT EXISTS idx_apps_price_rating_content_rating_category_id ON apps(price,rating,content_rating,category_id);")

        try:
            conn.execute(sql_create_index)
            conn.commit()
        except Exception as e:
            print(f"Failed to create index: {e}")
    
        df = pd.read_sql_query(query, con=conn)

    return df


import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder



# Main function to run the Streamlit app
def main():
    st.set_page_config(layout="wide", page_title="Google Play Store Dashboard")
    from streamlit_option_menu import option_menu

    selected = option_menu(
        menu_title=None,
        options=["Home", "Visualization","Trending", "Contact"],
        icons=["house", "book", "calender","envelope"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    
    st.sidebar.title("CRUD Operations")


    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Load your dataset (e.g., from CSV or database)
    query = "SELECT apps.*,categories.category as category FROM googleplay.apps Inner Join \
    googleplay.Categories ON apps.category_id=categories.category_id\
    ORDER BY apps.app_id LIMIT 150000"
    df = load_data(query)
    
    # Sidebar filters
    categories = ['All'] + list(df['category'].unique())
    selected_category = st.sidebar.selectbox("Select Category", categories, key='filter_selected_category',
                                             index=categories.index(st.session_state.get('filter_selected_category')) if\
                                               st.session_state.get('filter_selected_category') in categories else 0)
    
    # Filter by content rating
    content_ratings = ['All'] + list(df['content_rating'].unique())
    selected_content_rating = st.sidebar.selectbox("Select Content Rating", options=content_ratings, key='filter_selected_content_rating',
                                                   index=content_ratings.index(st.session_state.get('filter_selected_content_rating')) if\
                                               st.session_state.get('filter_selected_content_rating') in content_ratings else 0)
                                                   
    
    # Assuming df is your DataFrame containing the price data


    min_price = df['price'].min()
    max_price = df['price'].max()

    price_range = st.sidebar.slider(
        'Select Price Range',
        min_value=0.0,
        max_value=max_price,
        value=(min_price, max_price),
        key='filter_price_range'
    )

    min_rating = st.sidebar.number_input("Minimum Rating", 0.0, 5.0,
                                    value = st.session_state.get('filter_min_rating',0.0),
                                      key='filter_min_rating')
    
    free_apps_only = st.sidebar.checkbox('Show only free apps', value=True, key='filter_free_apps_only')

    
    def reset_filters():
        for key in st.session_state.keys():
            if key.startswith('filter_'):
                del st.session_state[key]
    
    reset_button = st.sidebar.button("Reset Filters", on_click=reset_filters)
    
    

    query = f"SELECT apps.*,categories.category as category FROM googleplay.apps Inner Join \
    googleplay.Categories ON apps.category_id=categories.category_id\
    WHERE apps.rating>={min_rating} AND \
     apps.price BETWEEN {price_range[0]} AND {price_range[1]} AND apps.free={free_apps_only}"
    # Apply filters
    if selected_category != 'All':
        query += f" AND category='{selected_category}' "
        if selected_content_rating !='All':
            query += f" AND apps.content_rating='{selected_content_rating}'"
    
    query += " ORDER BY apps.app_id DESC LIMIT 10000"

    start_time = time.time()
    filtered_df = load_data(query)
    end_time = time.time()
    st.write(f"Query took {end_time - start_time} seconds.")

    # Main content
    st.title("Google Play Store Dashboard")
    
    if selected=="Home":
        # Overview section
        st.header("Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Apps", len(filtered_df))
        col2.metric("Average Rating", f"{filtered_df['rating'].mean():.2f}")
        col3.metric("Free Apps", f"{(filtered_df['price'] == 0).sum()} ({(filtered_df['price'] == 0).mean():.1%})")
        
        # Data Grid section
        st.header("App Details")
        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
        gridOptions = gb.build()
        
        grid_response = AgGrid(
            filtered_df,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='streamlit', #Add theme color to the table
            enable_enterprise_modules=True,
            height=350, 
            width='100%',
            reload_data=True
        )

        # Top categories by number of apps
        category_counts = df['category'].value_counts().head(10)
        fig_top_categories = px.bar(category_counts, x=category_counts.index, y=category_counts.values,
                                        title="Top 10 Categories by Number of Apps",
                                        labels={"x": "Category", "y": "Number of Apps"},
                                        color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig_top_categories, use_container_width=True)
        
        
    if selected=='Visualization':
        # Visualizations section
        st.header("Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating distribution
            fig_rating_dist = px.histogram(filtered_df, x="rating", 
                                        title="Distribution of App Ratings",
                                        labels={"rating": "Rating", "count": "Number of Apps"},
                                        color_discrete_sequence=['#FFA500'])
            st.plotly_chart(fig_rating_dist, use_container_width=True)
        
        
        # Scatter plot: Rating vs. Reviews
        fig_scatter = px.scatter(filtered_df, x="rating_count", y="rating", 
                                title="App Ratings vs. Number of Reviews",
                                labels={"reviews": "Number of Reviews", "rating": "Rating"},
                                color="category", hover_name="app_name",
                                log_x=True)  # log scale for reviews due to wide range
        st.plotly_chart(fig_scatter, use_container_width=True)

    if selected=="Trending":
        st.header("Trending Categories")
        #Line Plot: Categories vs. Released Date
        if selected_category!='All':
            query  = f"SELECT app_id,released,c.category FROM googleplay.apps as a INNER JOIN googleplay.categories as c on \
            c.category_id = a.category_id WHERE c.category='{selected_category}';"
            df1 = load_data(query)
            df1['year'] = pd.to_datetime(df1['released']).dt.year #Extract Release Year
            category_year = df1.groupby('year').agg({'app_id':'count'}).reset_index()
            fig_line = px.bar(category_year, x='year', y='app_id',
                               title=f'Distribution of {selected_category} Apps Release vs. Years',
                               labels={"app_id":"Number of Apps"})
            
            st.plotly_chart(fig_line, use_container_width=True)


            query  = f"SELECT app_id,last_updated,c.category FROM googleplay.apps as a INNER JOIN googleplay.categories as c on \
            c.category_id = a.category_id WHERE c.category='{selected_category}';"
            df1 = load_data(query)
            df1['year'] = pd.to_datetime(df1['last_updated']).dt.year #Extract Release Year
            category_year = df1.groupby('year').agg({'app_id':'count'}).reset_index()
            fig_line = px.bar(category_year, x='year', y='app_id',
                               title=f'Distribution of {selected_category} Apps Updated vs. Years',
                               labels={"app_id":"Number of Apps"})
            
            st.plotly_chart(fig_line, use_container_width=True)


if __name__ == "__main__":
    main()



