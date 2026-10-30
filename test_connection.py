import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="cpsinghraghav1026",
        database="hostel_management"
    )

    if connection.is_connected():
        print("MySQL Connected Successfully!")
        print("Hostel Database is Ready.")

    connection.close()

except mysql.connector.Error as error:
    print("Connection Failed!")
    print(error)