"""
Polyglot Codebase Test Cases and Examples

Demonstrates multi-language analysis capabilities of Cartographer:
- JavaScript/TypeScript example
- Go example
- C# example
- Cross-language dependencies
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any


# Example JavaScript/TypeScript service
TYPESCRIPT_EXAMPLE = '''
import { Router, Request, Response } from 'express';
import { PaymentService } from './payment.service';

interface Order {
  id: string;
  amount: number;
  currency: string;
}

export class OrderController {
  constructor(private paymentService: PaymentService) {}

  async createOrder(req: Request, res: Response): Promise<void> {
    try {
      const order: Order = req.body;
      const result = await this.paymentService.processPayment(order);
      res.json({ success: true, result });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  getOrderById(id: string): Promise<Order> {
    // Implementation here
    return Promise.resolve({} as Order);
  }
}

export default OrderController;
'''

# Example Go microservice
GO_EXAMPLE = '''
package payment

import (
	"context"
	"database/sql"
	"log"

	"github.com/grpc-ecosystem/go-grpc-middleware"
	"google.golang.org/grpc"
)

type PaymentService struct {
	db *sql.DB
}

func NewPaymentService(db *sql.DB) *PaymentService {
	return &PaymentService{db: db}
}

func (s *PaymentService) ProcessPayment(ctx context.Context, amount float64) (string, error) {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return "", err
	}
	defer tx.Rollback()

	// Process payment logic
	transactionID := "TXN-12345"

	if err := tx.Commit(); err != nil {
		return "", err
	}

	return transactionID, nil
}

func (s *PaymentService) ValidatePayment(amount float64) bool {
	return amount > 0
}

// gRPC server setup
func StartPaymentServer(addr string) error {
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(grpc_middleware.ChainUnaryServer()),
	)

	RegisterPaymentServiceServer(grpcServer, &PaymentService{})

	return grpcServer.Serve(lis)
}
'''

# Example C#/.NET service
CSHARP_EXAMPLE = '''
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
using PaymentSystem.Models;
using PaymentSystem.Interfaces;

namespace PaymentSystem.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PaymentController : ControllerBase
    {
        private readonly IPaymentProcessor _paymentProcessor;
        private readonly ILogger<PaymentController> _logger;

        public PaymentController(
            IPaymentProcessor paymentProcessor,
            ILogger<PaymentController> logger)
        {
            _paymentProcessor = paymentProcessor;
            _logger = logger;
        }

        [HttpPost("process")]
        public async Task<IActionResult> ProcessPaymentAsync([FromBody] PaymentRequest request)
        {
            if (!ValidateRequest(request))
            {
                return BadRequest("Invalid payment request");
            }

            try
            {
                var result = await _paymentProcessor.ProcessAsync(request);
                _logger.LogInformation($"Payment processed: {result.TransactionId}");
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Payment processing failed");
                return StatusCode(500, "Payment processing failed");
            }
        }

        [HttpGet("{transactionId}")]
        public async Task<IActionResult> GetPaymentStatusAsync(string transactionId)
        {
            var status = await _paymentProcessor.GetStatusAsync(transactionId);
            return Ok(status);
        }

        private bool ValidateRequest(PaymentRequest request)
        {
            return request.Amount > 0 && !string.IsNullOrEmpty(request.Currency);
        }
    }

    public interface IPaymentProcessor
    {
        Task<PaymentResult> ProcessAsync(PaymentRequest request);
        Task<PaymentStatus> GetStatusAsync(string transactionId);
    }

    [Serializable]
    public class PaymentRequest
    {
        public decimal Amount { get; set; }
        public string Currency { get; set; }
        public string OrderId { get; set; }
    }

    public record PaymentResult(
        string TransactionId,
        bool Success,
        string Message
    );
}
'''

# Example Python backend service
PYTHON_EXAMPLE = '''
from flask import Flask, request, jsonify
from typing import Dict, Any
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)


class PaymentProcessor:
    """Core payment processing logic."""
    
    def __init__(self, gateway_client):
        self.gateway = gateway_client
    
    def process_payment(self, order_id: str, amount: float) -> Dict[str, Any]:
        """Process a payment transaction."""
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Invalid amount")
            
            # Call payment gateway
            txn = self.gateway.create_transaction(order_id, amount)
            
            # Log transaction
            logger.info(f"Payment processed: {txn['id']}")
            
            return {
                "transaction_id": txn["id"],
                "status": "completed",
                "amount": amount
            }
        except Exception as e:
            logger.error(f"Payment failed: {str(e)}")
            raise


# REST API routes
payment_processor = PaymentProcessor(gateway_client=None)


@app.route('/api/payments', methods=['POST'])
def create_payment():
    """Create a new payment."""
    data = request.json
    
    try:
        result = payment_processor.process_payment(
            data['order_id'],
            data['amount']
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/payments/<transaction_id>', methods=['GET'])
def get_payment_status(transaction_id):
    """Get payment status."""
    return jsonify({"status": "completed"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''


def create_polyglot_test_codebase(base_dir: str) -> Dict[str, str]:
    """
    Create a test polyglot codebase with multiple languages.

    Args:
        base_dir: Base directory for the test codebase

    Returns:
        Dictionary mapping relative file paths to their absolute paths
    """
    # Create directory structure
    structure = {
        'frontend/src': ['order.controller.ts', 'payment.service.ts'],
        'backend/go': ['payment_service.go', 'grpc.go'],
        'backend/dotnet': ['PaymentController.cs', 'IPaymentProcessor.cs'],
        'backend/python': ['payment_processor.py', 'api.py'],
    }

    created_files = {}

    # Create TypeScript files
    ts_dir = os.path.join(base_dir, 'frontend', 'src')
    os.makedirs(ts_dir, exist_ok=True)

    ts_file = os.path.join(ts_dir, 'order.controller.ts')
    with open(ts_file, 'w') as f:
        f.write(TYPESCRIPT_EXAMPLE)
    created_files['frontend/src/order.controller.ts'] = ts_file

    # Create Go files
    go_dir = os.path.join(base_dir, 'backend', 'go')
    os.makedirs(go_dir, exist_ok=True)

    go_file = os.path.join(go_dir, 'payment_service.go')
    with open(go_file, 'w') as f:
        f.write(GO_EXAMPLE)
    created_files['backend/go/payment_service.go'] = go_file

    # Create C# files
    cs_dir = os.path.join(base_dir, 'backend', 'dotnet')
    os.makedirs(cs_dir, exist_ok=True)

    cs_file = os.path.join(cs_dir, 'PaymentController.cs')
    with open(cs_file, 'w') as f:
        f.write(CSHARP_EXAMPLE)
    created_files['backend/dotnet/PaymentController.cs'] = cs_file

    # Create Python files
    py_dir = os.path.join(base_dir, 'backend', 'python')
    os.makedirs(py_dir, exist_ok=True)

    py_file = os.path.join(py_dir, 'payment_processor.py')
    with open(py_file, 'w') as f:
        f.write(PYTHON_EXAMPLE)
    created_files['backend/python/payment_processor.py'] = py_file

    return created_files


def test_multi_language_analysis():
    """Test multi-language analyzer with a polyglot example."""
    from agents.multi_language_analyzer import MultiLanguageAnalyzer, analyze_codebase

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='polyglot_test_')

    try:
        print(f"Creating test codebase in: {temp_dir}")
        files = create_polyglot_test_codebase(temp_dir)

        print(f"\nCreated {len(files)} test files:")
        for rel_path, abs_path in files.items():
            print(f"  - {rel_path}")

        # Analyze the codebase
        print("\n" + "="*60)
        print("ANALYZING POLYGLOT CODEBASE")
        print("="*60)

        analyzer = MultiLanguageAnalyzer()
        print(f"\nSupported languages: {analyzer.get_supported_languages()}")

        # Test individual file analysis
        print("\n" + "-"*60)
        print("Individual File Analysis")
        print("-"*60)

        for rel_path, abs_path in files.items():
            print(f"\nAnalyzing: {rel_path}")
            result = analyzer.analyze_file(abs_path)

            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                language = result.get('language')
                entities = result.get('entities', [])
                imports = result.get('imports', [])

                print(f"  Language: {language}")
                print(f"  Entities: {len(entities)}")
                if entities:
                    for entity in entities[:3]:
                        print(f"    - {entity.get('name')} ({entity.get('type')})")
                print(f"  Imports: {len(imports)}")

        # Test directory analysis
        print("\n" + "-"*60)
        print("Directory-Wide Analysis")
        print("-"*60)

        results = analyzer.analyze_directory(temp_dir, max_workers=4)

        print(f"\nTotal files analyzed: {results['total_files_analyzed']}")
        print(f"Files by language: {results['files_by_language']}")
        print(f"Cross-language dependencies: {len(results['cross_language_dependencies'])}")

        if results['cross_language_dependencies']:
            print("\nCross-language dependencies found:")
            for dep in results['cross_language_dependencies'][:3]:
                print(f"  {dep['source']['language']} -> {dep['target']['language']}")

        # Print statistics
        stats = results.get('statistics', {})
        print(f"\nCodebase Statistics:")
        print(f"  Total LOC: {stats.get('total_lines_of_code', 0)}")
        print(f"  Total Classes: {stats.get('total_classes', 0)}")
        print(f"  Total Functions: {stats.get('total_functions', 0)}")
        print(f"  Total Methods: {stats.get('total_methods', 0)}")

        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*60)

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up test directory: {temp_dir}")


if __name__ == '__main__':
    test_multi_language_analysis()
