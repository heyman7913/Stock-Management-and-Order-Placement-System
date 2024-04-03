import sys

from main import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        migrate = Migrate(app, db)

        command_line_args = sys.argv
        if len(command_line_args) > 1:
            try:
                if command_line_args[1] == "delete_admin":
                    try:
                        command = command_line_args[2]
                    except Exception as e:
                        command = BLANK
                    if command == "all":
                        admin_logins_db = AdminLogin.query.all()
                        for admin_login_db in admin_logins_db:
                            admin_details_db = AdminDetails.query.filter(
                                AdminDetails.admin_login_id == admin_login_db.id
                            ).first()
                            if admin_details_db is not None:
                                email_send_ref = EmailSend(
                                    thread_name="Admin Deletion",
                                    email=admin_details_db.emailID,
                                    subject=f"{server_name} | Admin Account Deleted",
                                    body=f"""
                                    Hi {admin_details_db.first_name},
    
                                    Your admin access for user {admin_details_db.emailID}
                                    has been revoked.
                                    Thanks for being a valued admin.
    
                                    Thanks and Regards,
                                    Bot.
                                    """,
                                )
                                email_send_ref.start()
                            db.session.delete(admin_login_db)
                        db.session.commit()
                        print(f"All Admins have been deleted")
                    else:
                        email = command
                        while email is BLANK:
                            email = input("Email Id : ")
                        admin_login_db = AdminLogin.query.filter(
                            AdminLogin.user_name == email.upper(),
                        ).first()

                        if admin_login_db is not None:
                            admin_details_db = AdminDetails.query.filter(
                                AdminDetails.admin_login_id == admin_login_db.id
                            ).first()
                            if admin_details_db is not None:
                                email_send_ref = EmailSend(
                                    thread_name="Admin Deletion",
                                    email=admin_details_db.emailID,
                                    subject=f"{server_name} | Admin Account Deleted",
                                    body=f"""
                                    Hi {admin_details_db.first_name},
            
                                    Your admin access for user {admin_details_db.emailID}
                                    has been revoked.
                                    Thanks for being a valued admin.
            
                                    Thanks and Regards,
                                    Bot.
                                    """,
                                )
                                email_send_ref.start()

                            db.session.delete(admin_login_db)
                            db.session.commit()
                            print(f"Admin {email} has been deleted")
                        else:
                            print(f"Admin {email} not found")
                elif command_line_args[1] == "create_admin":
                    first_name = command_line_args[2]
                    last_name = command_line_args[3]
                    email = command_line_args[4]
                    phone_no = command_line_args[5]
                    password = command_line_args[6]
                    while first_name is BLANK:
                        first_name = input("First Name : ")
                    while last_name is BLANK:
                        last_name = input("Last Name : ")
                    while email is BLANK:
                        email = input("Email Id : ")
                    while phone_no is BLANK:
                        phone_no = input("Phone Number : ")
                    while password is BLANK:
                        password = input("Password : ")
                    # Hash actual password
                    password_hash = hashlib.sha1()
                    password_hash.update(password.encode("utf-8"))
                    password_org = password
                    password = password_hash.hexdigest()
                    try:
                        admin_login_db = AdminLogin(
                            user_name=email.upper(),
                            password_hash=password,
                        )
                        db.session.add(admin_login_db)
                        db.session.commit()
                        db.session.refresh(admin_login_db)
                        admin_details_db = AdminDetails(
                            first_name=first_name,
                            last_name=last_name,
                            emailID=email,
                            phoneNumber=phone_no,
                            admin_login_id=admin_login_db.id,
                        )
                        db.session.add(admin_details_db)
                        db.session.commit()

                    except Exception as e:
                        print("Admin Creation Failed : \n" + str(e))
                    else:
                        email_send_ref = EmailSend(
                            thread_name="Admin Creation",
                            email=admin_details_db.emailID,
                            subject=f"{server_name} | Admin Account Created",
                            body=f"""
                            Hi {admin_details_db.first_name},
                            
                            Welcome to {server_name}
    
                            User ID : {admin_details_db.emailID}
                            Password : {password_org}
    
                            Thanks and Regards,
                            Bot.
                            """,
                        )
                        email_send_ref.start()

                        del admin_login_db
                        del admin_details_db
                        print("Admin Created")
                else:
                    pass
            except Exception as e:
                print(e)

        else:
            dir_path = os.path.join(PROJECT_DIR, "temp_files")
            for filename in os.listdir(dir_path):
                if filename == "do not delete":
                    continue
                else:
                    file_path = os.path.join(dir_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print("Failed to delete %s. Reason: %s" % (file_path, e))
                    else:
                        print("Temp file deleted : ", filename)
            print("Temp file(s) deleted")
            app.run(host=server_host, port=server_port, debug=server_stat)
