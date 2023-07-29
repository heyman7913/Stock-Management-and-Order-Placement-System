import sys

from main import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        migrate = Migrate(app, db)

        command_line_args = sys.argv
        if len(command_line_args) == 3:
            if command_line_args[1] == "delete_admin":
                if command_line_args[2] == "all":
                    admin_logins_db = AdminLogin.query.all()
                    for admin_login_db in admin_logins_db:
                        db.session.delete(admin_login_db)
                    db.session.commit()
                    print(f"All Admins have been deleted")
                else:
                    pass
            else:
                pass
        elif len(command_line_args) == 2:
            if command_line_args[1] == "delete_admin":
                email = BLANK
                while email is BLANK:
                    email = input("Email Id : ")
                admin_login_db = AdminLogin.query.filter(
                    AdminLogin.user_name == email.upper(),
                ).first()
                if admin_login_db is not None:
                    db.session.delete(admin_login_db)
                    db.session.commit()
                    print(f"Admin {email} has been deleted")
                else:
                    print(f"Admin {email} not found")
            elif command_line_args[1] == "create_admin":
                first_name = BLANK
                last_name = BLANK
                email = BLANK
                phone_no = BLANK
                password = BLANK
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
                password_hash.update(password.encode('utf-8'))
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
                    del admin_login_db
                    del admin_details_db
                except Exception as e:
                    print("Admin Creation Failed : \n" + str(e))
                else:
                    print("Admin Created")
            else:
                pass

        else:
            app.run(
                host=server_host,
                port=server_port,
                debug=server_stat
            )
