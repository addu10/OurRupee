# OurRupee - Crowdfunding Platform

OurRupee is a blockchain-integrated crowdfunding platform that enables users to create and contribute to donation campaigns securely. The platform leverages Auth0 for authentication and Ethereum smart contracts for transparent fund management.

## Features

- **Secure Authentication**: User authentication powered by Auth0
- **Campaign Creation**: Register new donation campaigns with detailed information
- **Donation System**: Contribute to campaigns with secure payment processing
- **Admin Dashboard**: Manage campaigns and view platform metrics
- **Blockchain Integration**: Ethereum smart contracts for transparent donation tracking
- **User Dashboard**: Track donation history and campaign participation

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML/CSS/JavaScript
- **Authentication**: Auth0
- **Database**: MySQL
- **Blockchain**: Ethereum (Solidity Smart Contracts)

## Getting Started

### Prerequisites

- Python 3.7+
- pip
- MySQL Server
- Node.js & npm (for blockchain interaction)
- Metamask or similar Ethereum wallet

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/OurRupee.git
   cd OurRupee
   ```

2. Install Python dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file in the root directory with the following variables:
   ```
   AUTH0_CLIENT_ID=your_auth0_client_id
   AUTH0_DOMAIN=your_auth0_domain.auth0.com
   AUTH0_CLIENT_SECRET=your_auth0_client_secret
   APP_SECRET_KEY=your_app_secret_key
   PORT=3000
   ```

4. Set up your MySQL database:
   - Create a database named `ourrupee`
   - Update the database configuration in `server.py` if needed

### Running the Application

Run the application locally with:
```
python server.py
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Auth0 Configuration

1. Create an Auth0 account and application at [Auth0](https://auth0.com)
2. Configure your Auth0 application:
   - Allowed Callback URLs: `http://localhost:3000/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins: `http://localhost:3000`

## Smart Contract Deployment

The project includes a Solidity smart contract for managing crowdfunding campaigns on the Ethereum blockchain:

1. Deploy the `CrowdFunding.sol` contract using Remix, Truffle, or Hardhat
2. Update the contract address in the application code

## Project Structure

- `server.py` - Main Flask application
- `templates/` - HTML templates for web pages
- `static/` - CSS, JavaScript, and other static assets
- `Smart Contract/` - Ethereum smart contracts
- `flask_session/` - Server-side session storage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
