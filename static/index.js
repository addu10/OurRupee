// Initialize ethers.js and contract variables
let provider;
let signer;
let contract;

// Contract address and ABI
const contractAddress = "0x30C000bc4eA1c8201b6FD1B895344a21fdbEE8AA"; // Your contract address
const contractABI = [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_owner",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_title",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_description",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_target",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_deadline",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_image",
				"type": "string"
			}
		],
		"name": "createCampaign",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "donateToCampaign",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "campaigns",
		"outputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "title",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "target",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "deadline",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "amountCollected",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "image",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getCampaigns",
		"outputs": [
			{
				"components": [
					{
						"internalType": "address",
						"name": "owner",
						"type": "address"
					},
					{
						"internalType": "string",
						"name": "title",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "description",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "target",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "deadline",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "amountCollected",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "image",
						"type": "string"
					},
					{
						"internalType": "address[]",
						"name": "donators",
						"type": "address[]"
					},
					{
						"internalType": "uint256[]",
						"name": "donations",
						"type": "uint256[]"
					}
				],
				"internalType": "struct CrowdFunding.Campaign[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "getDonators",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			},
			{
				"internalType": "uint256[]",
				"name": "",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "numberOfCampaigns",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
];

// Connect to MetaMask
async function connect() {
    if (typeof window.ethereum !== "undefined") {
        try {
            await ethereum.request({ method: "eth_requestAccounts" });
            provider = new ethers.providers.Web3Provider(window.ethereum);
            signer = provider.getSigner();
            contract = new ethers.Contract(contractAddress, contractABI, signer);
            document.getElementById("connectButton").innerHTML = "Connected";
            console.log("MetaMask connected:", await signer.getAddress());
        } catch (error) {
            console.error("Error connecting MetaMask:", error);
        }
    } else {
        document.getElementById("connectButton").innerHTML = "Please install MetaMask";
    }
}

// Create a new campaign
async function createCampaign(event) {
    event.preventDefault();
    const owner = document.getElementById("owner").value;
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const target = ethers.utils.parseEther(document.getElementById("target").value);
    const deadline = Math.floor(new Date(document.getElementById("deadline").value).getTime() / 1000);
    const image = document.getElementById("image").value;

    try {
        const tx = await contract.createCampaign(owner, title, description, target, deadline, image);
        await tx.wait(); // Wait for the transaction to be mined
    
        // Get the number of campaigns to determine the new campaign ID
        const campaignId = await contract.numberOfCampaigns() - 1;
    
        // Display the campaign ID
        const campaignIdDisplay = document.getElementById("campaignIdDisplay");
        campaignIdDisplay.innerHTML = `Campaign ID: ${campaignId}`;
        alert(`Campaign created with ID: ${campaignId}`);
    } catch (error) {
        console.error("Error creating campaign:", error);
    }
}

// Get all campaigns
async function getCampaigns() {
    try {
        const campaigns = await contract.getCampaigns();
        const campaignsList = document.getElementById("campaignsList");
        campaignsList.innerHTML = '';

        campaigns.forEach((campaign, index) => {
            const campaignElement = document.createElement('div');
            campaignElement.innerHTML = `
                <strong>Campaign ID:</strong> ${index}<br>
                <strong>Owner:</strong> ${campaign.owner}<br>
                <strong>Title:</strong> ${campaign.title}<br>
                <strong>Description:</strong> ${campaign.description}<br>
                <strong>Target (ETH):</strong> ${ethers.utils.formatEther(campaign.target)}<br>
                <strong>Amount Collected (ETH):</strong> ${ethers.utils.formatEther(campaign.amountCollected)}<br>
                <strong>Deadline:</strong> ${new Date(campaign.deadline * 1000).toLocaleString()}<br><br>
            `;
            campaignsList.appendChild(campaignElement);
        });
    } catch (error) {
        console.error("Error fetching campaigns:", error);
    }
}

// Collapse campaign details
function collapseCampaigns() {
    const campaignsList = document.getElementById("campaignsList");
    campaignsList.innerHTML = '';
}

// Get donators for a specific campaign
async function getDonators(event) {
    event.preventDefault();
    const campaignId = document.getElementById("donateCampaignId").value;

    try {
        const [donators, donations] = await contract.getDonators(campaignId);
        const donatorsList = document.getElementById("donatorsList");
        donatorsList.innerHTML = '<h4>Donators and Donations</h4>';

        donators.forEach((donator, index) => {
            const donatorElement = document.createElement('div');
            donatorElement.innerHTML = `
                <strong>Donator:</strong> ${donator}<br>
                <strong>Donation Amount (ETH):</strong> ${ethers.utils.formatEther(donations[index])}<br><br>
            `;
            donatorsList.appendChild(donatorElement);
        });
    } catch (error) {
        console.error("Error fetching donators:", error);
    }
}

// Donate to a campaign
async function donateToCampaign(event) {
    event.preventDefault();
    const campaignId = document.getElementById("campaignId").value;
    const donationAmount = ethers.utils.parseEther(document.getElementById("donationAmount").value);

    try {
        // Check if the campaign ID exists
        const campaignExists = await contract.campaigns(campaignId);
        if (!campaignExists) {
            throw new Error(`Campaign with ID ${campaignId} does not exist`);
        }

        // Donate to the campaign
        const tx = await contract.donateToCampaign(campaignId, { value: donationAmount });
        const receipt = await tx.wait();

        // Check if the transaction was successful
        if (receipt.status === 1) {
            alert("Donation successful!");
        } else {
            throw new Error("Transaction failed. Please try again.");
        }
    } catch (error) {
        const donationError = document.getElementById("donationError");
        donationError.innerHTML = error.message;
        donationError.style.display = "block";
    }
}

// Attach event listeners
document.getElementById("createCampaignForm").addEventListener("submit", createCampaign);
document.getElementById("donatorsForm").addEventListener("submit", getDonators);
document.getElementById("donateForm").addEventListener("submit", donateToCampaign);
