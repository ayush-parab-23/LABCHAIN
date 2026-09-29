// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LabChain
 * @dev Manages the medical report hashes and their lifecycle/versions on the blockchain.
 */
contract LabChain {
    address public owner;

    enum ReportStatus { ACTIVE, SUPERSEDED, REVOKED }

    struct ReportRecord {
        string reportHash;
        string labId;
        uint256 timestamp;
        uint256 version;
        ReportStatus status;
        bool exists;
    }

    // Maps reportId -> version -> ReportRecord
    mapping(string => mapping(uint256 => ReportRecord)) private reports;
    // Maps reportId -> currentVersion
    mapping(string => uint256) private currentVersions;
    // Maps reportId -> exists
    mapping(string => bool) private reportExists;
    // Maps reportId -> labId
    mapping(string => string) private reportLabs;

    event ReportRegistered(string indexed reportId, string reportHash, string labId, uint256 version, uint256 timestamp);
    event ReportVersionUpdated(string indexed reportId, string reportHash, uint256 version, uint256 timestamp);
    event ReportStatusChanged(string indexed reportId, uint256 version, ReportStatus status, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Registers a new medical report with version 1.
     */
    function registerReport(
        string memory _reportId,
        string memory _reportHash,
        string memory _labId,
        uint256 _timestamp
    ) public {
        require(!reportExists[_reportId], "Report already exists");

        reports[_reportId][1] = ReportRecord({
            reportHash: _reportHash,
            labId: _labId,
            timestamp: _timestamp,
            version: 1,
            status: ReportStatus.ACTIVE,
            exists: true
        });

        currentVersions[_reportId] = 1;
        reportExists[_reportId] = true;
        reportLabs[_reportId] = _labId;

        emit ReportRegistered(_reportId, _reportHash, _labId, 1, _timestamp);
    }

    /**
     * @dev Updates an existing report to a new version, marking the old one as SUPERSEDED.
     */
    function updateReportVersion(
        string memory _reportId,
        string memory _newHash,
        uint256 _timestamp
    ) public {
        require(reportExists[_reportId], "Report does not exist");
        
        uint256 currentVer = currentVersions[_reportId];
        require(reports[_reportId][currentVer].status == ReportStatus.ACTIVE, "Report version is not active");

        // Mark current version as superseded
        reports[_reportId][currentVer].status = ReportStatus.SUPERSEDED;
        emit ReportStatusChanged(_reportId, currentVer, ReportStatus.SUPERSEDED, _timestamp);

        // Register new version
        uint256 newVer = currentVer + 1;
        reports[_reportId][newVer] = ReportRecord({
            reportHash: _newHash,
            labId: reportLabs[_reportId],
            timestamp: _timestamp,
            version: newVer,
            status: ReportStatus.ACTIVE,
            exists: true
        });

        currentVersions[_reportId] = newVer;

        emit ReportVersionUpdated(_reportId, _newHash, newVer, _timestamp);
    }

    /**
     * @dev Revokes a report entirely.
     */
    function revokeReport(string memory _reportId, uint256 _timestamp) public {
        require(reportExists[_reportId], "Report does not exist");
        uint256 currentVer = currentVersions[_reportId];
        require(reports[_reportId][currentVer].status == ReportStatus.ACTIVE, "Report version is not active");

        reports[_reportId][currentVer].status = ReportStatus.REVOKED;
        emit ReportStatusChanged(_reportId, currentVer, ReportStatus.REVOKED, _timestamp);
    }

    /**
     * @dev Retrieves report version details.
     * Passing 0 for _version returns the latest current version.
     */
    function getReport(string memory _reportId, uint256 _version) public view returns (
        string memory reportHash,
        string memory labId,
        uint256 timestamp,
        uint256 version,
        uint8 status,
        bool exists
    ) {
        require(reportExists[_reportId], "Report does not exist");
        uint256 ver = _version == 0 ? currentVersions[_reportId] : _version;
        ReportRecord memory rec = reports[_reportId][ver];
        require(rec.exists, "Version does not exist");
        return (rec.reportHash, rec.labId, rec.timestamp, rec.version, uint8(rec.status), rec.exists);
    }

    /**
     * @dev Gets the latest version number of a report.
     */
    function getLatestVersion(string memory _reportId) public view returns (uint256) {
        require(reportExists[_reportId], "Report does not exist");
        return currentVersions[_reportId];
    }
}
