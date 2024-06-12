# import os
# import json
# from passlib.hash import pbkdf2_sha256
# from Utils.auth_utils import generate_jwt_token, log_login, log_logout, validate_jwt_token
# from bson import ObjectId
# from fastapi import HTTPException
# from datetime import datetime
# from s3_utils import upload_to_s3


# class UserDataHandler:
#     def __init__(self, username, password, email, otp_handler):
#         self.username = username
#         self.password = password
#         self.email = email
#         self.otp_handler = otp_handler


#     async def authenticate_user(self, db):
#         try:
#             # Check if the user exists
#             user = await db.user.find_one({"email_id": self.email})

#             if not user:
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

#             hashed_password = user['password_hash']


#             # Verify the password
#             if not pbkdf2_sha256.verify(self.password, hashed_password):
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

#             # Generate a JWT token
#             token_data = generate_jwt_token(self.username)

#             # Log the login time
#             token_data = log_login(self.username, token_data)

#             session_start = await db.session.insert_one(token_data)

#             return {'statusCode': 200,
#                     'body': json.dumps({'message': 'Login successful', 'session_start': str(session_start),
#                                         'session_token': token_data['token']})}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in authenticate_user: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def logout_user(self, db, token):
#         try:
#             # Validate the JWT token
#             decoded_token = validate_jwt_token(token)

#             if decoded_token and decoded_token['sub'] == self.username:
#                 # Search for the user's session record
#                 session_record = await db.session.find_one({"username": self.username})

#                 if session_record:
#                     # Log the logout time and obtain token data
#                     token_data = log_logout(decoded_token['sub'], session_record)

#                     # Append token_data to the existing session record
#                     updated_session_record = {**session_record, **token_data}

#                     # Update the user's session record in the database
#                     await db.session.update_one({"username": self.username}, {"$set": updated_session_record})

#                     return {'statusCode': 200, 'body': json.dumps({'message': 'Logout successful'})}

#                 else:
#                     return {'statusCode': 404, 'body': json.dumps({'message': 'User session not found'})}
#             else:
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in logout_user: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def put_user_data(self, db):
#         try:
#             # Insert new user data into MongoDB
#             user_data = {
#                 "user_name": self.username,
#                 "email_id": self.email,
#                 "password_hash": pbkdf2_sha256.hash(self.password),
#             }
#             result = await db.user.insert_one(user_data)
#             # Call put_profile_picture to upload the profile picture
#             #await self.put_profile_picture(db, str(result.inserted_id))

#             # Send OTP
#             #await self.otp_handler.send_otp_sms(email=self.email, username=self.username)

#             return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in put_user_data: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def get_user_data(self, db):
#         try:
#             # Retrieve user data based on username
#             user_data = await db.user.find_one({"user_name": self.username})

#             if user_data:
#                 return {
#                     "user_data": {
#                         "user_name": user_data["user_name"],
#                         "email_id": user_data["email_id"],
#                         "profile_picture": user_data.get("profile_picture", None),
#                     }
#                 }
#             else:
#                 raise HTTPException(status_code=404, detail="User not found")
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in get_user_data: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def put_profile_picture(self, db, user_id, image_data):
#         try:
#             # Upload image to S3 using the utility function
#             bucket_name = os.environ.get('S3_BUCKET_NAME')
#             file_name = f"{user_id}.png"  # Assuming the image is in PNG format
#             s3_url = upload_to_s3(bucket_name, file_name, image_data)

#             # Update user data in the database with the S3 URL
#             await db.user.update_one({"user_name": self.username}, {"$set": {"profile_picture": s3_url}})

#             return {"message": "Profile picture uploaded successfully"}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in put_profile_picture: {str(e)}")
#             return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

# # Example usage:
# # user_handler = UserDataHandler(username="john_doe", password="password123", email="john_doe@example.com")
# # response = user_handler.authenticate_user(db)
# # print(response)
import json
from passlib.hash import pbkdf2_sha256
from Utils.auth_utils import generate_jwt_token, log_login, log_logout, validate_jwt_token
from fastapi import HTTPException, File, UploadFile
from Utils.s3_utils import upload_to_s3
import logging
from fastapi.responses import JSONResponse
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserDataHandler:
    def __init__(self, username, password, email, otp_handler):
        self.username = username
        self.password = password
        self.email = email
        self.otp_handler = otp_handler

    async def authenticate_user(self, db):
        try:
            # Check if the user exists
            user = await db.user.find_one({"email_id": self.email})

            if not user:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

            hashed_password = user['password_hash']

            # Verify the password
            if not pbkdf2_sha256.verify(self.password, hashed_password):
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

            # Generate a JWT token
            country = user.get('country')
            job = user.get('job')
            token_data = generate_jwt_token(self.username,self.email,country, job)

            # Log the login time
            token_data = log_login(self.username,self.email,token_data)
            token_data['email'] = self.email  # Add the email to the token data

            existing_session = await db.session.find_one({"email": self.email,"active": False})
            if existing_session:
                await db.session.update_one({"_id": existing_session["_id"]}, {"$set": token_data, "$unset": {"logout_time": ""}})
            else:
                await db.session.insert_one(token_data)

            return {'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Login successful',
                        'session_token': token_data['token'],
                        'user_details': {
                            'country': country,
                            'job': job,
                            'username': self.username
                        }
                    })}

        except Exception as e:
            # Log the exception
            print(f"Exception in authenticate_user: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def logout_user(self, db, token):
        try:
            # Validate the JWT token
            decoded_token = validate_jwt_token(token)
            print(f"Decoded token: {decoded_token}")

            if decoded_token and decoded_token['email'] == self.email:
                # Search for the user's session record
                # session_record = await db.session.find_one({"username": self.username})
                email = decoded_token.get('email')
                if not email:
                    return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid token: email not found'})}

                # Search for the user's session record based on the email
                session_record = await db.session.find_one({"email": email})
                print("session_record",session_record)

                if session_record:
                    # Log the logout time and obtain token data
                    token_data = log_logout(decoded_token['email'], session_record)

                    # Append token_data to the existing session record
                    updated_session_record = {**session_record, **token_data}
                    updated_session_record.pop('_id', None)
                    updated_session_record['logout_time'] = token_data['logout_time']  # Set logout time
                    print(updated_session_record)

                    # Update the user's session record in the database
                    await db.session.update_one({"email": email}, {"$set": updated_session_record})

                    return {'statusCode': 200, 'body': json.dumps({'message': 'Logout successful'})}

                else:
                    return {'statusCode': 404, 'body': json.dumps({'message': 'User session not found'})}
            else:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
        except Exception as e:
            # Log the exception
            print(f"Exception in logout_user: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def get_token_by_email(self, db, email):
        try:
            # Search for the user's session record based on the email
            session_record = await db.session.find_one({"email": email})

            if session_record:
                # Extract the token from the session record
                token = session_record.get("token")
                return {'statusCode': 200, 'body': json.dumps({'token': token})}
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Token not found for the provided email'})}
        except Exception as e:
            # Log the exception
            print(f"Exception in get_token_by_email: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}


    async def forgot_password(self, db, event: dict):
        try:
            # data = await request.json()
            email = event["email"]
            if not email:
                raise HTTPException(status_code=400, detail="Email is required")

            user = await db.user.find_one({"email_id": email})
            if not user:
                raise HTTPException(status_code=404, detail="Email not found")

            response = await self.otp_handler.send_otp_sms(email, user["user_name"])
            return JSONResponse(content=response)
        except HTTPException as http_exc:
            logger.error(f"HTTP error occurred: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def reset_password(self, db, event: dict):
        try:
            email = event["email"]
            otp = event["otp"]
            new_password = event["new_password"]

            if not email or not otp or not new_password:
                raise HTTPException(status_code=404, detail="Email, OTP, and new password are required")

            otp_response = await self.otp_handler.validate_otp_message(email, otp)

            if isinstance(otp_response, str):
                # If otp_response is a string, it means there was an error.
                raise HTTPException(status_code=400, detail=otp_response)
            else:
                # Otherwise, otp_response is a dictionary.
                if otp_response["statusCode"] != 200:
                    raise HTTPException(status_code=otp_response["statusCode"], detail=otp_response["body"])

                password_hash = pbkdf2_sha256.hash(new_password)
                await db.user.update_one({"email_id": email}, {"$set": {"password_hash": password_hash}})

                return {"message": "Password reset successfully"}
        except HTTPException as http_exc:
            logger.error(f"HTTP error occurred: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


    # async def put_user_data(self, db):
    #     try:
    #         # Insert new user data into MongoDB
    #         user_data = {
    #             "user_name": self.username,
    #             "email_id": self.email,
    #             "password_hash": pbkdf2_sha256.hash(self.password),
    #         }
    #
    #         # TODO: check if a user with the same email id exists already -> if so then return an error status
    #
    #         result = await db.user.insert_one(user_data)
    #         # Create a new document for user preferences
    #         user_preferences = {
    #             "email_id": self.email,
    #             "preferred_dates": [],
    #             "preferred_countries": [],
    #         }
    #         await db.user_preferences.insert_one(user_preferences)
    #
    #         # Call put_profile_picture to upload the profile picture
    #         # await self.put_profile_picture(db, str(result.inserted_id))
    #
    #         # Send OTP
    #         # await self.otp_handler.send_otp_sms(email=self.email, username=self.username)
    #
    #         return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
    #     except Exception as e:
    #         # Log the exception
    #         print(f"Exception in put_user_data: {str(e)}")
    #         return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}
    async def put_user_data(self, db, image_data=None):
        try:
            # Insert new user data into MongoDB
            user_data = {
                "user_name": self.username,
                "email_id": self.email,
                "password_hash": pbkdf2_sha256.hash(self.password),
            }

            # Check if a user with the same email id exists already
            if await self.user_exists(db, self.email):
                return {'statusCode': 400, 'body': json.dumps({'message': 'User with this email already exists'})}

            result = await db.user.insert_one(user_data)

            # Create a new document for user preferences
            user_preferences = {
                "email_id": self.email,
                "preferred_dates": [],
                "preferred_countries": [],
            }
            await db.user_preferences.insert_one(user_preferences)

            # Call put_profile_picture to upload the profile picture
            if image_data:
                await self.put_profile_picture(db, str(result.inserted_id), image_data=image_data)

            # Send OTP
            await self.otp_handler.send_otp_sms(self.email, self.username)

            return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_user_data: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def user_exists(self, db, email):
        return await db.user.find_one({"email_id": email}) is not None

    async def send_otp_sms(self):
        # Assuming implementation for sending OTP SMS
        pass

    async def get_user_preferences(self, db, email):
        try:
            # Retrieve user preferences based on email
            user_preferences = await db.user_preferences.find_one({"email_id": email})

            if user_preferences:
                return {
                    "preferred_dates": user_preferences.get("preferred_dates", []),
                    "preferred_countries": user_preferences.get("preferred_countries", []),
                }
            else:
                return {"message": "User preferences not found"}
        except Exception as e:
            # Log the exception
            print(f"Exception in get_user_preferences: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def update_user_preferences(self, db, email, preferred_dates=None, preferred_countries=None):
        try:
            # Check if user preferences record exists
            existing_record = await db.user_preferences.find_one({"email_id": email})

            if existing_record:
                # Update user preferences
                await db.user_preferences.update_one(
                    {"email_id": email},
                    {"$set": {
                        "preferred_dates": preferred_dates if preferred_dates else [],
                        "preferred_countries": preferred_countries if preferred_countries else [],
                    }}
                )
                return {"message": "User preferences updated successfully"}
            else:
                # Insert new user preferences record
                await db.user_preferences.insert_one({
                    "email_id": email,
                    "preferred_dates": preferred_dates if preferred_dates else [],
                    "preferred_countries": preferred_countries if preferred_countries else [],
                })
                return {"message": "New user preferences record created successfully"}

        except Exception as e:
            # Log the exception
            print(f"Exception in update_user_preferences: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}


    async def get_user_data(self, db):
        try:
            # Retrieve user data based on username
            user_data = await db.user.find_one({"email_id": self.email})

            if user_data:
                return {
                    "user_data": {
                        "user_name": user_data["user_name"],
                        "email_id": user_data["email_id"],
                        "profile_picture": user_data.get("profile_picture", None),
                        "job": user_data.get("job", None),
                        "country": user_data.get("country", None),
                        "linkedin": user_data.get("linkedin", None),
                    }
                }
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            # Log the exception
            print(f"Exception in get_user_data: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    # async def put_profile_picture(self, db, user_id, image_data):
    #     try:
    #         # Upload image to S3 using the utility function
    #         bucket_name = os.environ.get('S3_BUCKET_NAME')
    #         file_name = f"{user_id}.png"  # Assuming the image is in PNG format
    #         s3_url = upload_to_s3(bucket_name, file_name, image_data)
    #
    #         # Update user data in the database with the S3 URL
    #         await db.user.update_one({"user_name": self.username}, {"$set": {"profile_picture": s3_url}})
    #
    #         return {"message": "Profile picture uploaded successfully"}
    #     except Exception as e:
    #         # Log the exception
    #         print(f"Exception in put_profile_picture: {str(e)}")
    #         return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}
    # async def put_profile_picture(self, db, user_id, image_data):
    #     try:
    #         # Assuming image_data is a file-like object or a file path
    #         # If image_data is a file path, open the file in binary mode
    #         if isinstance(image_data, str):  # Check if image_data is a file path
    #             with open(image_data, 'rb') as file:
    #                 image_data = file.read()

    #         # Upload image to S3 using the utility function
    #         bucket_name = os.environ.get('S3_BUCKET_NAME')
    #         file_name = f"{user_id}.png"  # Assuming the image is in PNG format
    #         s3_url = upload_to_s3(bucket_name, file_name, image_data)

    #         # Update user data in the database with the S3 URL
    #         await db.user.update_one({"user_name": self.username}, {"$set": {"profile_picture": s3_url}})

    #         return {"message": "Profile picture uploaded successfully"}
    #     except Exception as e:
    #         # Log the exception
    #         print(f"Exception in put_profile_picture: {str(e)}")
    #         return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}
    async def put_profile_picture(self, db, email: str, file: UploadFile = File(...)):
        try:
            # Extract file extension
            _, file_extension = os.path.splitext(file.filename)
            # Upload image to S3 using the utility function
            bucket_name = os.environ.get('S3_BUCKET_NAME')
            file_name = f"{email}_profile_picture{file_extension}"
            # s3_url = upload_to_s3(bucket_name, file_name, image_data)
            s3_url = upload_to_s3(bucket_name, file_name, file.file)

            # Update user data in the database with the S3 URL
            # await db.user.update_one({"email_id": self.email}, {"$set": {"profile_picture": s3_url}})

            return f"{s3_url}"
        except Exception as e:
            # Log the exception
            print(f"Exception in put_profile_picture: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

    async def put_residence(self, db, residence):
        try:
            # Update user data in the database with the residence
            await db.user.update_one({"email_id": self.email}, {"$set": {"country": residence}})
            return {"message": "Residence updated successfully"}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_residence: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

    async def put_job(self, db, job):
        try:
            # Update user data in the database with the job
            await db.user.update_one({"email_id": self.email}, {"$set": {"job": job}})
            return {"message": "Job updated successfully"}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_job: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

    async def put_linkedin(self, db, url):
        try:
            # Update user data in the database with the job
            await db.user.update_one({"email_id": self.email}, {"$set": {"linkedin": url}})
            return {"message": "Job updated successfully"}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_job: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

    async def fetch_group_members(self, db, trip_id: str):
        try:
            # Find the messaging room for the given trip ID
            messaging_room = await db["messaging_room"].find_one({"trip_id": trip_id})
            if messaging_room:
                # Fetch participants with joined=true from messaging_room
                messaging_room_joined = await db["messaging_room"].find_one(
                    {"trip_id": trip_id, "messages.joined": True}
                )
                if messaging_room_joined:
                    messages = messaging_room_joined.get("messages", [])
                    print(messages)

                    # Get the last joined user
                    last_joined_message = next(
                        (
                            message
                            for message in reversed(messages)
                            if "joined" in message and message["joined"]
                        ),
                        None,
                    )
                    print("last_joined_message", last_joined_message)
                    # Fetch user details for users who have not left
                    valid_emails = set()
                    for message in messages:
                        if "joined" in message and message["joined"]:
                            # Ensure message["sender"] is a string before adding it to the set
                            if isinstance(message["sender"], str):
                                valid_emails.add(message["sender"])
                        if "left" in message and message["left"]:
                            # Ensure message["sender"] is a string before removing it from the set
                            if isinstance(message["sender"], str):
                                valid_emails.discard(message["sender"])

                        sender = message.get("sender")
                        if sender and isinstance(sender, list) and message.get(
                                "message") == "Has been added to the trip Successfully":
                            # Iterate over each email in the list and add it to the set
                            for email in sender:
                                if isinstance(email, str):
                                    valid_emails.add(email)

                    group_members = []
                    for email in valid_emails:
                        user = await db["user"].find_one({"email_id": email})
                        if user:
                            # Extract required fields from user data
                            user_data = {
                                "user_name": user["user_name"],
                                "email_id": user["email_id"],
                                "profile_picture": user["profile_picture"],
                                "job": user["job"],
                                "country": user["country"]
                            }
                            group_members.append(user_data)
                            print(user_data)

                    return {"group_members": group_members}
                else:
                    return {"group_members": []}  # Return empty list if no participants with joined=true
            else:
                return {"group_members": []}  # Return empty list if no messaging room found for the trip ID
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


# Example usage:
# user_handler = UserDataHandler(username="john_doe", password="password123", email="john_doe@example.com")
# response = user_handler.authenticate_user(db)
# print(response)

