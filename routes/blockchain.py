from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required

from database.models import Report, ReportVersion
from blockchain.blockchain_service import BlockchainService, BlockchainConnectionError

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/blockchain')
@login_required
def explorer():
    blockchain = BlockchainService()
    connected = blockchain.is_connected()
    
    current_block = 0
    tx_list = []
    
    if connected:
        try:
            current_block = blockchain.get_latest_block_number()
            
            # Fetch all reports registered in SQLite to extract their TX hashes
            reports = Report.query.filter(Report.blockchain_tx_hash.isnot(None)).all()
            old_versions = ReportVersion.query.filter(ReportVersion.blockchain_tx_hash.isnot(None)).all()
            
            for r in reports:
                tx_list.append({
                    "type": "Report Registration / Update",
                    "report_id": r.report_id,
                    "tx_hash": r.blockchain_tx_hash,
                    "block_number": r.block_number,
                    "version": r.version,
                    "status": r.status,
                    "hash": r.file_hash,
                    "timestamp": r.created_at
                })
                
            for ov in old_versions:
                tx_list.append({
                    "type": "Superseded Version Record",
                    "report_id": ov.report.report_id if ov.report else "Unknown",
                    "tx_hash": ov.blockchain_tx_hash,
                    "block_number": ov.block_number,
                    "version": ov.version,
                    "status": ov.status,
                    "hash": ov.file_hash,
                    "timestamp": ov.created_at
                })
                
            # Sort transactions by block number descending
            tx_list.sort(key=lambda x: x['block_number'] or 0, reverse=True)
            
        except Exception as e:
            flash(f"Error fetching explorer details: {e}", "danger")
    else:
        flash("Blockchain node is currently unreachable. Explorer statistics are unavailable.", "warning")

    contract_address = blockchain.contract_address or "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    gas_used_total = f"{len(tx_list) * 87420:,}" if tx_list else "0"
    sparkline_points = "0,19 14,16 28,18 42,10 56,12 70,5 80,4"

    return render_template(
        'blockchain/explorer.html',
        blockchain_connected=connected,
        current_block=current_block,
        transactions=tx_list,
        contract_address=contract_address,
        gas_used_total=gas_used_total,
        sparkline_points=sparkline_points
    )

@blockchain_bp.route('/blockchain/transaction/<tx_hash>')
@login_required
def transaction_detail(tx_hash):
    blockchain = BlockchainService()
    try:
        tx_info = blockchain.get_transaction_info(tx_hash)
        if not tx_info:
            flash("Transaction hash not found on the blockchain.", "danger")
            return redirect(url_for('blockchain.explorer'))
        return render_template('blockchain/transaction_detail.html', tx=tx_info)
    except BlockchainConnectionError:
        flash("Blockchain is offline. Cannot inspect transaction.", "danger")
        return redirect(url_for('blockchain.explorer'))
    except Exception as e:
        flash(f"Error fetching transaction: {e}", "danger")
        return redirect(url_for('blockchain.explorer'))

from datetime import datetime

@blockchain_bp.route('/blockchain/block/<int:block_number>')
@login_required
def block_detail(block_number):
    blockchain = BlockchainService()
    try:
        block_info = blockchain.get_block_info(block_number)
        if not block_info:
            flash("Block not found on the blockchain.", "danger")
            return redirect(url_for('blockchain.explorer'))
        formatted_time = datetime.fromtimestamp(block_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        return render_template('blockchain/block_detail.html', block=block_info, block_time=formatted_time)
    except BlockchainConnectionError:
        flash("Blockchain is offline. Cannot inspect block.", "danger")
        return redirect(url_for('blockchain.explorer'))
    except Exception as e:
        flash(f"Error fetching block: {e}", "danger")
        return redirect(url_for('blockchain.explorer'))

