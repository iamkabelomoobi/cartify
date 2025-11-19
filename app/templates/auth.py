def get_otp_email_template(otp_code: str, user_email: str) -> str:
    """Generate HTML template for OTP email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; margin-top: 20px; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #4CAF50; text-align: center; 
                        letter-spacing: 5px; padding: 20px; background: white; border-radius: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛒 Cartify</h1>
            </div>
            <div class="content">
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>You requested to reset your password for your Cartify account (<strong>{user_email}</strong>).</p>
                <p>Use the following OTP code to complete your password reset:</p>
                <div class="otp-code">{otp_code}</div>
                <p><strong>This code will expire in 10 minutes.</strong></p>
                <p>If you didn't request this password reset, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Cartify. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_welcome_email_template(user_name: str, user_email: str) -> str:
    """Generate HTML template for welcome email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; margin-top: 20px; }}
            .button {{ background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none;
                      border-radius: 5px; display: inline-block; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛒 Welcome to Cartify!</h1>
            </div>
            <div class="content">
                <h2>Hi {user_name}! 👋</h2>
                <p>Thank you for registering with Cartify.</p>
                <p>Your account has been successfully created with the email: <strong>{user_email}</strong></p>
                <p>You can now start shopping and enjoying our services!</p>
                <p>If you have any questions, feel free to reach out to our support team.</p>
            </div>
            <div class="footer">
                <p>© 2024 Cartify. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_password_reset_success_email_template(user_email: str) -> str:
    """Generate HTML template for password reset success email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; margin-top: 20px; }}
            .success-icon {{ font-size: 48px; text-align: center; padding: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛒 Cartify</h1>
            </div>
            <div class="content">
                <div class="success-icon">✅</div>
                <h2>Password Reset Successful</h2>
                <p>Hello,</p>
                <p>Your password for your Cartify account (<strong>{user_email}</strong>) has been successfully reset.</p>
                <p>You can now log in with your new password.</p>
                <p>If you did not perform this action, please contact our support team immediately.</p>
            </div>
            <div class="footer">
                <p>© 2024 Cartify. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
