import streamlit as st
import pandas as pd
from app import url_object
from sqlalchemy import create_engine
import plotly.express as px
from streamlit_extras.switch_page_button import switch_page


def load_data(query):

    engine = create_engine(url_object,execution_options={"schema_translate_map": {None: "public"}})
    conn = engine.connect()

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
        options=["Home", "Visualization", "Contact"],
        icons=["house", "book", "envelope"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    
    st.sidebar.title("CRUD Operations")
    st.sidebar.markdown("[Create](./CRUD/create.py)")
    st.sidebar.markdown("[Read](./CRUD/read.py)")
    st.sidebar.markdown("[Update](./CRUD/update.py)")
    st.sidebar.markdown("[Delete](./CRUD/delete.py)")

    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Load your dataset (e.g., from CSV or database)
    df = load_data("SELECT googleplay.apps.*,googleplay.categories.category FROM googleplay.apps Inner Join googleplay.Categories ON \
                   googleplay.apps.category_id=googleplay.categories.category_id LIMIT 500;")
    
    # Sidebar filters
    categories = ['All'] + list(df['category'].unique())
    selected_category = st.sidebar.selectbox("Select Category", categories, key='filter_category')
    
    # Filter by content rating
    content_ratings = df['content_rating'].unique()
    selected_content_rating = st.sidebar.selectbox("Select Content Rating", options=["All"] + list(content_ratings), key='filter_content_rating',
                                                   )
    
    # Assuming df is your DataFrame containing the price data


    min_price = df['price'].min()
    max_price = df['price'].max()

    if min_price == max_price:
        max_price+=1.0

    price_range = st.sidebar.slider(
        'Select Price Range',
        min_value=0.0,
        max_value=max_price,
        value=st.session_state.get('filter_price_range', (0.0, max_price)),
        key='filter_price_range'
    )



    min_rating, max_rating = df['rating'].min(), df['rating'].max()

    min_rating = st.sidebar.slider("Minimum Rating", min_rating, max_rating,
                                    value = st.session_state.get('filter_min_rating', 0.0),
                                      key='filter_min_rating')
    
    free_apps_only = st.sidebar.checkbox('Show only free apps', value=False, key='filter_free_apps_only')

    #max_price = st.sidebar.number_input("Maximum Price", 0.0, value = float(df['price'].max()))

    def reset_filters():
        for key in st.session_state.keys():
            if key.startswith('filter_'):
                del st.session_state[key]
    
    reset_button = st.sidebar.button("Reset Filters", on_click=reset_filters)
    


    # Apply filters
    if selected_category != 'All':
        filtered_df = df[(df['category'] == selected_category) & 
                         (df['rating'] >= min_rating) & 
                         ((df['price'] >= price_range[0]) & (df['price'] < price_range[1])) &
                           ((df['content_rating']==selected_content_rating) | (selected_content_rating=='All')&
                            (df['free']==free_apps_only))
                           ]
    else:
        filtered_df = df[(df['rating'] >= min_rating) & 
                         ((df['price'] >= price_range[0]) & (df['price'] < price_range[1]))&
                         ((df['content_rating']==selected_content_rating) | (selected_content_rating=='All'))&
                         (df['free']==free_apps_only)]
        
    
    
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
        
        with col2:
            # Top categories by number of apps
            category_counts = filtered_df['category'].value_counts().head(10)
            fig_top_categories = px.bar(category_counts, x=category_counts.index, y=category_counts.values,
                                        title="Top 10 Categories by Number of Apps",
                                        labels={"x": "Category", "y": "Number of Apps"},
                                        color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig_top_categories, use_container_width=True)
        
        # Scatter plot: Rating vs. Reviews
        fig_scatter = px.scatter(filtered_df, x="rating_count", y="rating", 
                                title="App Ratings vs. Number of Reviews",
                                labels={"reviews": "Number of Reviews", "rating": "Rating"},
                                color="category", hover_name="app_name",
                                log_x=True)  # log scale for reviews due to wide range
        st.plotly_chart(fig_scatter, use_container_width=True)




if __name__ == "__main__":
    main()



