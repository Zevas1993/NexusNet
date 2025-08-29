#!/usr/bin/env python3
"""Federated Learning Client Implementation"""

from __future__ import annotations
import requests
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class FederatedLearningClient:
    """Client for secure federated learning participation"""

    def __init__(self, client_id: str, coordinator_url: str,
                 private_key_path: Optional[str] = None):
        self.client_id = client_id
        self.coordinator_url = coordinator_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30

        # Load or generate cryptographic keys
        self.private_key = self._load_private_key(private_key_path)
        self.public_key = self.private_key.public_key()

        # Client state
        self.registered = False
        self.model_version = 0
        self.last_sync = None
        self.participation_count = 0

        logger.info(f"Federated learning client {client_id} initialized")

    def _load_private_key(self, key_path: Optional[str] = None) -> rsa.RSAPrivateKey:
        """Load or generate private key for secure communication"""
        if key_path and Path(key_path).exists():
            try:
                with open(key_path, 'rb') as f:
                    return serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
            except Exception as e:
                logger.error(f"Failed to load private key: {e}")

        # Generate new key pair
        logger.info("Generating new private key for federated learning client")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Save if path provided
        if key_path:
            os.makedirs(Path(key_path).parent, exist_ok=True)
            with open(key_path, 'wb') as f:
                pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                f.write(pem)

        return private_key

    def register(self) -> bool:
        """Register with coordinator and establish secure connection"""
        try:
            # Serialize public key
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            registration_data = {
                "client_id": self.client_id,
                "public_key": public_pem.decode(),
                "capabilities": {
                    "supported_formats": ["gradient", "model_update"],
                    "max_batch_size": 1000,
                    "encryption_support": True
                }
            }

            # Sign registration request
            signature = self._sign_data(json.dumps(registration_data, sort_keys=True))

            payload = {
                "registration": registration_data,
                "signature": signature.hex()
            }

            response = self.session.post(
                f"{self.coordinator_url}/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 201:
                result = response.json()
                self.registered = True
                logger.info(f"Successfully registered with coordinator: {result.get('status')}")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def get_model_updates(self) -> Optional[Dict[str, Any]]:
        """Request current model updates from coordinator"""
        if not self.registered:
            logger.error("Client not registered")
            return None

        try:
            params = {
                "client_id": self.client_id,
                "current_version": self.model_version
            }

            response = self.session.get(
                f"{self.coordinator_url}/model-updates",
                params=params
            )

            if response.status_code == 200:
                updates = response.json()
                if self._verify_coordinator_signature(updates):
                    self.model_version = updates.get("version", self.model_version)
                    self.last_sync = time.time()
                    return updates

            elif response.status_code == 304:  # Not Modified
                logger.debug("No new model updates available")
                return None
            else:
                logger.warning(f"Failed to get updates: {response.status_code}")

        except Exception as e:
            logger.error(f"Error getting model updates: {e}")

        return None

    def submit_contribution(self, gradients: Dict[str, Any],
                          sample_count: int) -> bool:
        """Submit federated learning contribution to coordinator"""
        if not self.registered:
            logger.error("Client not registered")
            return False

        try:
            # Prepare contribution data
            contribution_data = {
                "client_id": self.client_id,
                "version": self.model_version,
                "sample_count": sample_count,
                "gradients": self._mask_gradients(gradients),
                "timestamp": time.time(),
                "metrics": {
                    "accuracy": 0.0,  # Would be computed locally
                    "loss": 0.0,
                    "samples_processed": sample_count
                }
            }

            # Sign contribution
            data_to_sign = json.dumps({
                "client_id": contribution_data["client_id"],
                "version": contribution_data["version"],
                "sample_count": contribution_data["sample_count"],
                "timestamp": contribution_data["timestamp"]
            }, sort_keys=True)

            signature = self._sign_data(data_to_sign)

            payload = {
                "contribution": contribution_data,
                "signature": signature.hex()
            }

            response = self.session.post(
                f"{self.coordinator_url}/contribute",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                self.participation_count += 1
                logger.info(f"Successfully submitted contribution: {result.get('status')}")
                return True
            else:
                logger.error(f"Contribution failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Contribution error: {e}")
            return False

    def _mask_gradients(self, gradients: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential privacy masking to gradients"""
        # This is a simplified implementation
        # In production, would use more sophisticated DP techniques
        masked = {}

        for layer, gradient in gradients.items():
            if isinstance(gradient, list):
                # Add Laplace noise for differential privacy
                masked[layer] = [g + self._add_noise() for g in gradient]
            else:
                masked[layer] = gradient + self._add_noise()

        return masked

    def _add_noise(self, epsilon: float = 0.1, sensitivity: float = 1.0) -> float:
        """Add Laplace noise for differential privacy"""
        import random
        import math

        beta = sensitivity / epsilon
        u = random.random() - 0.5
        noise = -beta * math.copysign(1, u) * math.log(1 - 2 * abs(u))

        return noise

    def _sign_data(self, data: str) -> bytes:
        """Sign data with private key"""
        try:
            return self.private_key.sign(
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except Exception as e:
            logger.error(f"Failed to sign data: {e}")
            raise

    def _verify_coordinator_signature(self, data: Dict[str, Any]) -> bool:
        """Verify coordinator signature (would need coordinator's public key)"""
        # In production, this would verify the coordinator's signature
        # For now, we'll assume the coordinator response is authentic
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            "client_id": self.client_id,
            "registered": self.registered,
            "model_version": self.model_version,
            "participation_count": self.participation_count,
            "last_sync": self.last_sync,
            "uptime_seconds": time.time() - getattr(self, '_start_time', time.time())
        }

    def disconnect(self):
        """Clean disconnect from coordinator"""
        if self.registered:
            try:
                response = self.session.post(f"{self.coordinator_url}/disconnect")
                logger.info(f"Disconnection response: {response.status_code}")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.session.close()
                self.registered = False

def create_federated_client(client_id: str,
                          coordinator_url: str,
                          key_path: Optional[str] = None) -> FederatedLearningClient:
    """Factory function for creating federated learning clients"""
    return FederatedLearningClient(client_id, coordinator_url, key_path)

def aggregate_contributions(contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate client contributions using secure aggregation"""
    # This would implement Byzantine-robust aggregation
    # For now, return a simple average

    if not contributions:
        return {}

    aggregated = {}
    weight_sum = sum(contrib.get("sample_count", 1) for contrib in contributions)

    # Collect all layer keys
    all_layers = set()
    for contrib in contributions:
        all_layers.update(contrib.get("gradients", {}).keys())

    # Aggregate gradients by layer
    for layer in all_layers:
        layer_gradients = []
        layer_weights = []

        for contrib in contributions:
            if layer in contrib.get("gradients", {}):
                layer_gradients.append(contrib["gradients"][layer])
                layer_weights.append(contrib.get("sample_count", 1))

        if layer_gradients:
            aggregated[layer] = weighted_average(layer_gradients, layer_weights)

    return aggregated

def weighted_average(values: List[float], weights: List[float]) -> float:
    """Compute weighted average"""
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    return sum(v * w for v, w in zip(values, weights)) / total_weight

# Example usage:
"""
# Create and use a federated learning client
client = create_federated_client(
    client_id="client_001",
    coordinator_url="https://fl-coordinator.example.com",
    key_path="keys/fl_client.key"
)

if client.register():
    # Participate in federated learning
    updates = client.get_model_updates()
    if updates:
        # Train local model and submit contribution
        local_gradients = {"layer1": [0.1, 0.2], "layer2": [0.3, 0.4]}
        client.submit_contribution(local_gradients, sample_count=100)

    client.disconnect()
"""
