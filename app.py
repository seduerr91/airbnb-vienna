import pandas as pd
import streamlit as st
import plotly.express as px

# deployment instructions: https://towardsdatascience.com/from-streamlit-to-heroku-62a655b7319

@st.cache
def get_data():
    return pd.read_csv("http://data.insideairbnb.com/austria/vienna/vienna/2020-06-16/visualisations/listings.csv")

df = get_data()
st.title("Vienna AirBnB Analysis")

st.header("Visit these top sights in Vienna")
pics = {
    "St. Stephan's Cathedral": "https://images.unsplash.com/photo-1516550893923-42d28e5677af?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1652&q=80",
    "Schoenbrunn Gardens": "https://images.unsplash.com/photo-1588836807555-ec6dfa2fefd2?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1567&q=80",
    "Castle Belvedere": "https://images.unsplash.com/photo-1526581671404-349f224db79b?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60"
}
pic = st.selectbox("Choose Sight of Vienna", list(pics.keys()), 0)
st.image(pics[pic], use_column_width=True, caption=pics[pic])

st.subheader("Table overview available AirBnBs in Vienna")
st.markdown("Following are the top five most expensive properties.")
defaultcols = ["name", "host_name", "neighbourhood", "room_type", "price"]
cols = st.multiselect("Columns", df.columns.tolist(), default=defaultcols)
st.dataframe(df[cols].head(20))

st.header("Where are the most expensive properties located?")
st.subheader("On a map")
st.markdown("The following map shows the top 1% most expensive Airbnbs priced at $800 and above.")
st.map(df.query("price>=800")[["latitude", "longitude"]].dropna(how="any"))

st.header("Average price by room type")
st.table(df.groupby("room_type").price.mean().reset_index()\
    .round(2).sort_values("price", ascending=False)\
    .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

st.header("Which host has the most properties listed?")
listingcounts = df.host_id.value_counts()
top_host_1 = df.query('host_id==@listingcounts.index[0]')
top_host_2 = df.query('host_id==@listingcounts.index[1]')
st.write(f"""**{top_host_1.iloc[0].host_name}** is at the top with {listingcounts.iloc[0]} property listings.
**{top_host_2.iloc[1].host_name}** is second with {listingcounts.iloc[1]} listings. """)

st.header("What is the distribution of property price?")
values = st.sidebar.slider("Price range", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (50., 300.))
f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Price distribution")
f.update_xaxes(title="Price")
f.update_yaxes(title="No. of listings")
st.plotly_chart(f)

st.header("Properties by number of reviews")
st.write("Enter a range of numbers in the sidebar to view properties whose review count falls in that range.")
minimum = st.sidebar.number_input("Minimum", min_value=0.00)
maximum = st.sidebar.number_input("Maximum", min_value=0.00, value=5.00)
if minimum > maximum:
    st.error("Please enter a valid range")
else:
    df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
        .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]
