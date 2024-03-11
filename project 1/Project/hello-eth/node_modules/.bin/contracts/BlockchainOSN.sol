pragma solidity >= 0.8.11 <= 0.8.11;

contract BlockchainOSN {
    string public signup_details;
    string public publish_dtweets;
    
       
    //call this function to save new user details data to Blockchain
    function setSignup(string memory sd) public {
       signup_details = sd;	
    }
   //get Signup details
    function getSignup() public view returns (string memory) {
        return signup_details;
    }

    //call this function to save publish tweets to Blockchain
    function setPublishTweets(string memory pt) public {
       publish_dtweets = pt;	
    }
   //get publish tweets details
    function getPublishTweets() public view returns (string memory) {
        return publish_dtweets;
    }

   constructor() public {
        signup_details="";
	publish_dtweets="";
    }
}