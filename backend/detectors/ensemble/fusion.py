import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, List

class AttentionFusionNetwork(nn.Module):
    """
    Lightweight cross-attention block to intelligently weigh expert models based on their confidence.
    """
    def __init__(self, num_experts: int, embed_dim: int = 16):
        super().__init__()
        # Map (score, confidence) into embedding space
        self.input_proj = nn.Linear(2, embed_dim)
        
        # Query vector (represents the "what is fake" concept)
        self.query = nn.Parameter(torch.randn(1, embed_dim))
        
        # Attention mechanism
        self.key_proj = nn.Linear(embed_dim, embed_dim)
        self.value_proj = nn.Linear(embed_dim, embed_dim)
        
        # Final decision MLP
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.ReLU(),
            nn.Linear(embed_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor):
        # x shape: (batch_size, num_experts, 2)
        batch_size = x.size(0)
        
        # Embed inputs: (batch, num_experts, embed_dim)
        embeddings = self.input_proj(x)
        
        # Compute keys and values
        keys = self.key_proj(embeddings)
        values = self.value_proj(embeddings)
        
        # Expand query for batch: (batch, 1, embed_dim)
        q = self.query.expand(batch_size, -1, -1)
        
        # Attention scores: (batch, 1, num_experts)
        attn_scores = torch.bmm(q, keys.transpose(1, 2)) / (keys.size(-1) ** 0.5)
        attn_weights = F.softmax(attn_scores, dim=-1)
        
        # Context vector: (batch, 1, embed_dim)
        context = torch.bmm(attn_weights, values)
        
        # Squeeze and project to final logits: (batch, 1)
        logits = self.mlp(context.squeeze(1))
        
        return logits, attn_weights.squeeze(1)


class EnsembleFusion:
    """
    Fuses outputs from all 11 domains into a single decision using Attention.
    """
    def __init__(self, use_learned_fusion: bool = False):
        self.use_learned_fusion = use_learned_fusion
        self.num_experts = 11
        
        # Ordered list of all possible expert keys
        self.expert_keys = [
            "spatial_cnn", "temporal_rnn", "metadata", "frequency", "audio", 
            "lipsync", "rppg", "eye_reflection", "diffusion", "head_pose", "provenance"
        ]
        
        if self.use_learned_fusion:
            try:
                self.model = AttentionFusionNetwork(num_experts=self.num_experts)
                # In production, we would load weights: self.model.load_state_dict(...)
                self.model.eval()
            except Exception:
                self.use_learned_fusion = False

        # Fallback static weights
        self.static_weights = {
            "spatial_cnn": 0.15,
            "temporal_rnn": 0.15,
            "metadata": 0.05,
            "frequency": 0.10,
            "audio": 0.10,
            "lipsync": 0.15,
            "rppg": 0.05,
            "eye_reflection": 0.05,
            "diffusion": 0.05,
            "head_pose": 0.10,
            "provenance": 0.05
        }

    def analyze(self, detector_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes the dictionary of all executed detectors and returns a final verdict + explainability.
        """
        all_reasons = []
        raw_scores = {}
        
        for name, result in detector_results.items():
            all_reasons.extend(result.get("reasons", []))
            raw_scores[name] = result.get("score", 0.0)

        if self.use_learned_fusion:
            # Prepare tensor for attention model
            input_data = []
            for key in self.expert_keys:
                if key in detector_results:
                    input_data.append([
                        detector_results[key].get("score", 0.0),
                        detector_results[key].get("confidence", 0.0)
                    ])
                else:
                    # Missing expert, pad with 0
                    input_data.append([0.0, 0.0])
            
            x = torch.tensor([input_data], dtype=torch.float32)
            
            with torch.no_grad():
                logits, attn_weights = self.model(x)
                final_probability = torch.sigmoid(logits).item()
                weights = attn_weights[0].tolist()
                
            # Find the top contributor for explainability
            top_idx = max(range(len(weights)), key=weights.__getitem__)
            top_expert = self.expert_keys[top_idx]
            top_weight = weights[top_idx]
            
            if top_weight > 0.15:
                all_reasons.append(f"Top Contributor: {top_expert} ({top_weight*100:.1f}%)")
                
        else:
            # Fallback to static weights
            combined_score = 0.0
            total_weight = 0.0
            
            for name, result in detector_results.items():
                score = result.get("score", 0.0)
                confidence = result.get("confidence", 0.0)
                weight = self.static_weights.get(name, 0.0)
                
                adjusted_weight = weight * confidence
                combined_score += score * adjusted_weight
                total_weight += adjusted_weight
                
            final_probability = combined_score / total_weight if total_weight > 0 else 0.0

        return {
            "score": final_probability,
            "reasons": all_reasons,
            "raw_scores": raw_scores
        }
