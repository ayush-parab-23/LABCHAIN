const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying LabChain contract...");
  const LabChain = await hre.ethers.getContractFactory("LabChain");
  const contract = await LabChain.deploy();
  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log("LabChain deployed to:", contractAddress);

  // Get the ABI and bytecode
  const artifactPath = path.join(__dirname, "../artifacts/contracts/LabChain.sol/LabChain.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

  // Save the contract details
  const contractInfo = {
    address: contractAddress,
    abi: artifact.abi
  };

  const outputPath = path.join(__dirname, "../contract_info.json");
  fs.writeFileSync(outputPath, JSON.stringify(contractInfo, null, 2), "utf8");
  console.log("Contract info written to:", outputPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
