import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from gtts import gTTS
import pygame
import os
from io import BytesIO

# Load dataset
df = pd.read_csv("final_updated_maharashtra_agriculture_data.csv")

# Initialize and fit label encoders
le_city = LabelEncoder()
le_soil = LabelEncoder()
le_crop = LabelEncoder()

# Encode the labels for cities, soil types, and crops
df["City"] = le_city.fit_transform(df["City"])
df["Soil Type"] = le_soil.fit_transform(df["Soil Type"])
df["Best Crop"] = le_crop.fit_transform(df["Best Crop"])

# Define features and targets
X = df[["City", "Soil Type", "Fertilizer Cost", "Total Cultivating Cost"]]
y_crop = df["Best Crop"]
y_income = df["Income per Acre"]

# Split the data into training and testing sets
X_train, X_test, y_crop_train, y_crop_test, y_income_train, y_income_test = train_test_split(
    X, y_crop, y_income, test_size=0.2, random_state=42
)

# Train Random Forest models
model_income = RandomForestRegressor(n_estimators=100, random_state=42)
model_income.fit(X_train, y_income_train)

model_crop = RandomForestClassifier(n_estimators=100, random_state=42)
model_crop.fit(X_train, y_crop_train)


# Function to make predictions and provide feedback
def predict_crop_and_income(city, soil_type, fertilizer_cost, total_cultivating_cost):
    # Handle unseen labels
    try:
        city_encoded = le_city.transform([city])[0]
        soil_encoded = le_soil.transform([soil_type])[0]
    except ValueError as e:
        return None, None, f"Error: {str(e)}"

    input_data = [[city_encoded, soil_encoded, fertilizer_cost, total_cultivating_cost]]

    # Predict income
    predicted_income = model_income.predict(input_data)[0]

    # Predict crop
    predicted_crop_encoded = model_crop.predict(input_data)[0]

    try:
        predicted_crop = le_crop.inverse_transform([predicted_crop_encoded])[0]
    except ValueError as e:
        return None, None, f"Error: {str(e)}"

    # Prepare feedback text
    feedback_text = (
        f"Based on your inputs, the recommended crop is {predicted_crop} "
        f"with an expected income of {predicted_income:.2f} per acre."
    )

    return predicted_crop, predicted_income, feedback_text


# Function to generate and play voice feedback
def speak(text):
    tts = gTTS(text=text, lang='en')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(audio_fp, "mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# Function to visualize crop prices
def visualize_crop_prices():
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="Soil Type", y="Income per Acre", data=df, ax=ax)
    ax.set_title("Income per Acre for Different Soil Types")
    ax.set_xticklabels(le_soil.classes_, rotation=45)
    st.pyplot(fig)


# Function to plot bar chart for analysis
def plot_bar_chart(city, fertilizer_cost, total_cultivating_cost, predicted_income):
    parameters = ["Fertilizer Cost", "Total Cultivating Cost", "Predicted Income per Acre"]
    values = [fertilizer_cost, total_cultivating_cost, predicted_income]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=parameters, y=values, palette="viridis", ax=ax)
    ax.set_title(f"Analysis for {city} - Soil Type")
    ax.set_ylabel("Value")
    ax.set_ylim(10000, 80000)

    for i, v in enumerate(values):
        ax.text(i, v + 1000, str(v), ha='center', va='bottom', fontsize=10, color='black')

    st.pyplot(fig)


# Main function
def main():
    st.title("Agricultural Finance Advisor with ML Predictions")

    # Sidebar inputs
    st.sidebar.title("Input Parameters")
    city = st.sidebar.text_input("Enter your city", value="Thane")
    soil_type = st.sidebar.selectbox("Select your soil type", le_soil.classes_)
    fertilizer_cost = st.sidebar.number_input("Enter your fertilizer cost", min_value=0.0, value=4000.0)
    total_cultivating_cost = st.sidebar.number_input("Enter your total cultivating cost", min_value=0.0, value=4000.0)

    if st.sidebar.button("Get Advice"):
        predicted_crop, predicted_income, feedback_text = predict_crop_and_income(
            city, soil_type, fertilizer_cost, total_cultivating_cost
        )
        st.subheader("Prediction")
        st.write(feedback_text)

        # Provide voice feedback
        speak(feedback_text)

        st.subheader("Crop Prices Visualization")
        visualize_crop_prices()

        st.subheader("Analysis: Bar Chart")
        plot_bar_chart(city, fertilizer_cost, total_cultivating_cost, predicted_income)


if __name__ == "__main__":
    main()
