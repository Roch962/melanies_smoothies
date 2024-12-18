import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

# Get the active session and query the table
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.subheader("Fruit Options Table")
# st.dataframe(data=my_dataframe,use_container_width=True)

# st.stop()

#convert the Snowpark Dataframe to a pandas dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop
fruit_list = [row['FRUIT_NAME'] for row in my_dataframe.collect()]


# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Concatenate selected ingredients into a string
    for fruit_chosen in ingredients_list:
        ingredients_string +=fruit_chosen + ''

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
        sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    # Create the SQL insert statement
    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        "VALUES ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    # Display the SQL statement for debugging
    st.write(my_insert_stmt)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")


# st.text(smoothiefroot_response.json())
