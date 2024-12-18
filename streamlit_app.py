import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App title and instructions
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Name input for the smoothie
name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write(f'The name on your smoothie will be: **{name_on_order}**')

# Step 1: Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Step 2: Query Snowflake table and convert to Pandas for flexibility
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Display the table for debugging (optional)
# st.dataframe(pd_df)

# Step 3: Multiselect dropdown for choosing ingredients
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Step 4: Display results for chosen fruits
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Combine chosen fruits for the SQL statement

    # Loop through the selected fruits
    for fruit_chosen in ingredients_list:
        # Get the SEARCH_ON value for the chosen fruit
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # Display the clean "Search value" sentence
        st.write(f"The search value for **{fruit_chosen}** is **{search_on_value}**.")
        
        # Add a subheader for Nutrition Information (future API integration)
        st.subheader(f"{fruit_chosen} Nutrition Information")
        st.write("⚠️ *API not connected yet, so data will appear here later.*")

    # Display a simulated SQL statement for order creation
    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )
    st.subheader("Order Preview:")
    st.code(my_insert_stmt, language='sql')

    # Submit button for the order
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie has been ordered, {name_on_order}!", icon="✅")
