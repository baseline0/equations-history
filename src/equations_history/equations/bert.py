"""BERT equations: scaled dot-product attention and masked language modeling.

Source of truth for BERT mathematical definitions. Includes attention mechanism,
positional embeddings, and pretraining losses.
"""

import sympy as sp
from dataclasses import dataclass


@dataclass
class Equation:
    """Container for an equation with metadata."""
    name: str
    latex: str
    description: str
    history: str
    citations: list[str]
    source_line: int
    concepts: list[str]


class BERTEquations:
    """BERT transformer equations."""

    # Symbols
    Q = sp.Symbol("Q", real=False)  # Query matrix
    K = sp.Symbol("K", real=False)  # Key matrix
    V = sp.Symbol("V", real=False)  # Value matrix
    d_k = sp.Symbol("d_k", positive=True, integer=True)  # Key dimension
    T = sp.Symbol("T", positive=True, integer=True)  # Sequence length
    h = sp.Symbol("h", positive=True, integer=True)  # Number of heads
    d_model = sp.Symbol("d_model", positive=True, integer=True)  # Model dimension
    W_O = sp.Symbol("W_O", real=False)  # Output projection
    x = sp.Symbol("x", real=False)  # Token
    t = sp.Symbol("t", positive=True, integer=True)  # Position

    @staticmethod
    def scaled_dot_product_attention() -> Equation:
        """Scaled dot-product attention mechanism.

        Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V

        Source: bert.py:30
        """
        return Equation(
            name="Scaled Dot-Product Attention",
            latex=r"\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V",
            description=(
                "Core attention mechanism in Transformers. Queries attend to keys, "
                "weighted by softmax similarity, then aggregate values. "
                "Scaling by 1/√d_k stabilizes gradients."
            ),
            history=(
                "Introduced in 'Attention is All You Need' (Vaswani et al., 2017). "
                "The scaled dot-product attention replaced recurrence with parallelizable attention, "
                "enabling the Transformer architecture. The 1/√d_k scaling was crucial for training stability; "
                "without it, attention weights in high dimensions tend to produce vanishing gradients."
            ),
            citations=[
                "Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). "
                "Attention is All You Need. NeurIPS.",
            ],
            source_line=30,
            concepts=["attention", "self-attention", "transformer", "mechanism"],
        )

    @staticmethod
    def multi_head_attention() -> Equation:
        """Multi-head attention: concatenate multiple attention heads.

        MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W^O
        head_i = Attention(Q * W_i^Q, K * W_i^K, V * W_i^V)

        Source: bert.py:55
        """
        return Equation(
            name="Multi-Head Attention",
            latex=(
                r"\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O, "
                r"\quad \text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)"
            ),
            description=(
                "Extend scaled dot-product attention to multiple independent 'heads', "
                "each attending over different subspaces. Linearly project and concatenate."
            ),
            history=(
                "Multi-head attention (Vaswani et al., 2017) allows the model to attend to different "
                "representation subspaces. Each head learns different aspects of relationships; "
                "for example, one head might attend to syntax, another to semantics. "
                "This parallel processing is key to BERT's expressiveness."
            ),
            citations=[
                "Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). "
                "Attention is All You Need. NeurIPS.",
            ],
            source_line=55,
            concepts=["multi-head", "subspace", "representation"],
        )

    @staticmethod
    def positional_encoding() -> Equation:
        """Positional encoding: sine/cosine positional embeddings.

        PE(t, 2i) = sin(t / 10000^(2i/d_model))
        PE(t, 2i+1) = cos(t / 10000^(2i/d_model))

        Source: bert.py:80
        """
        return Equation(
            name="Positional Encoding (Sinusoidal)",
            latex=(
                r"\text{PE}(t, 2i) = \sin\left(\frac{t}{10000^{2i/d_\text{model}}}\right), \quad "
                r"\text{PE}(t, 2i+1) = \cos\left(\frac{t}{10000^{2i/d_\text{model}}}\right)"
            ),
            description=(
                "Inject position information into embeddings using sinusoidal functions. "
                "Different frequencies for each dimension allow the model to learn relative positions."
            ),
            history=(
                "Vaswani et al. (2017) introduced sinusoidal positional encodings to encode sequence order "
                "without recurrence. The choice of sin/cos with exponentially increasing frequencies "
                "enables learning of relative position relationships. BERT later adopted learned positional embeddings "
                "(absolute position embeddings), which are simpler and often equally effective for BERT's pretraining setup."
            ),
            citations=[
                "Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). "
                "Attention is All You Need. NeurIPS.",
                "Devlin, J., Chang, M-W., Lee, K., & Toutanova, K. (2018). "
                "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. "
                "arXiv:1810.04805.",
            ],
            source_line=80,
            concepts=["position", "embedding", "sequence order"],
        )

    @staticmethod
    def masked_language_modeling_loss() -> Equation:
        """Masked Language Modeling (MLM) loss.

        L_MLM = -sum_{t in masked} log P(x_t | x_{-t}; θ)

        Source: bert.py:105
        """
        return Equation(
            name="Masked Language Modeling (MLM) Loss",
            latex=r"\mathcal{L}_\text{MLM} = -\sum_{t \in \text{masked}} \log P(x_t \mid x_{\setminus t}; \theta)",
            description=(
                "Randomly mask 15% of tokens in the input. "
                "Train the model to predict masked tokens from context. "
                "Negative log-likelihood over masked positions."
            ),
            history=(
                "MLM is BERT's main pretraining objective (Devlin et al., 2018). "
                "Masking forces bidirectional context modeling: each token sees left and right context. "
                "This differs from left-to-right LMs (GPT) which can only condition on past tokens. "
                "The bidirectional pretraining makes BERT powerful for downstream tasks that benefit from "
                "full-context understanding (e.g., sentiment analysis, NER)."
            ),
            citations=[
                "Devlin, J., Chang, M-W., Lee, K., & Toutanova, K. (2018). "
                "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. "
                "arXiv:1810.04805.",
            ],
            source_line=105,
            concepts=["masked language modeling", "pretraining", "bidirectional", "prediction"],
        )

    @staticmethod
    def next_sentence_prediction_loss() -> Equation:
        """Next Sentence Prediction (NSP) loss (original BERT).

        L_NSP = -[y * log P(IsNext) + (1-y) * log P(NotNext)]

        Source: bert.py:130
        """
        return Equation(
            name="Next Sentence Prediction (NSP) Loss",
            latex=(
                r"\mathcal{L}_\text{NSP} = -[y \log p_\theta(\text{IsNext}) + "
                r"(1-y)\log p_\theta(\text{NotNext})]"
            ),
            description=(
                "Binary classification objective. Given two sentences, predict whether B follows A. "
                "Used in original BERT pretraining (now optional in later models)."
            ),
            history=(
                "NSP (Devlin et al., 2018) was designed to help BERT learn sentence-level relationships. "
                "However, later research (e.g., RoBERTa) showed NSP provides less benefit than continuous "
                "pretraining without it. Modern variants often drop NSP in favor of longer, contiguous "
                "text sequences. MLM remains the core pretraining signal across all Transformer variants."
            ),
            citations=[
                "Devlin, J., Chang, M-W., Lee, K., & Toutanova, K. (2018). "
                "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. "
                "arXiv:1810.04805.",
                "Liu, Y., Ott, M., Goyal, N., et al. (2019). "
                "RoBERTa: A Robustly Optimized BERT Pretraining Approach. arXiv:1907.11692.",
            ],
            source_line=130,
            concepts=["NSP", "sentence prediction", "binary classification"],
        )

    @staticmethod
    def bert_total_pretraining_loss() -> Equation:
        """Total BERT pretraining loss (combining MLM and NSP).

        L_BERT = L_MLM + L_NSP

        Source: bert.py:155
        """
        return Equation(
            name="BERT Total Pretraining Loss",
            latex=r"\mathcal{L}_\text{BERT} = \mathcal{L}_\text{MLM} + \mathcal{L}_\text{NSP}",
            description=(
                "Combine MLM and NSP losses during pretraining. "
                "Equal weighting (both contribute equally to gradient updates)."
            ),
            history=(
                "The combined loss in original BERT (Devlin et al., 2018) balances two learning signals: "
                "token-level understanding (MLM) and sentence-level understanding (NSP). "
                "In practice, MLM typically dominates (higher loss magnitude), but both guide learning. "
                "Later models often drop or modify NSP based on empirical results."
            ),
            citations=[
                "Devlin, J., Chang, M-W., Lee, K., & Toutanova, K. (2018). "
                "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. "
                "arXiv:1810.04805.",
            ],
            source_line=155,
            concepts=["pretraining", "loss", "combined objective"],
        )

    @staticmethod
    def bert_fine_tuning() -> Equation:
        """Fine-tuning strategy: add task-specific layer on top of [CLS] token.

        y = softmax(W_task * [CLS] + b_task)

        Source: bert.py:175
        """
        return Equation(
            name="BERT Fine-Tuning (Pooled Representation)",
            latex=r"y = \text{softmax}(W_\text{task} \cdot [\text{CLS}] + b_\text{task})",
            description=(
                "After pretraining, fine-tune BERT on downstream tasks. "
                "Use the [CLS] token (special classification token at sequence start) as "
                "a pooled representation, pass through a task-specific linear layer."
            ),
            history=(
                "BERT's fine-tuning approach (Devlin et al., 2018) is remarkably simple: "
                "the [CLS] token naturally aggregates information from all tokens via attention, "
                "and a single linear layer on top often suffices for classification. "
                "This simplicity enables BERT to transfer to many downstream tasks with minimal task-specific architecture. "
                "The pretrained representations are already rich; only the classifier head needs retraining."
            ),
            citations=[
                "Devlin, J., Chang, M-W., Lee, K., & Toutanova, K. (2018). "
                "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. "
                "arXiv:1810.04805.",
            ],
            source_line=175,
            concepts=["fine-tuning", "transfer learning", "classification", "downstream task"],
        )


# Convenience exports
def get_all_equations() -> dict[str, Equation]:
    """Return all BERT equations."""
    return {
        "scaled_dot_product_attention": BERTEquations.scaled_dot_product_attention(),
        "multi_head_attention": BERTEquations.multi_head_attention(),
        "positional_encoding": BERTEquations.positional_encoding(),
        "masked_language_modeling_loss": BERTEquations.masked_language_modeling_loss(),
        "next_sentence_prediction_loss": BERTEquations.next_sentence_prediction_loss(),
        "bert_total_pretraining_loss": BERTEquations.bert_total_pretraining_loss(),
        "bert_fine_tuning": BERTEquations.bert_fine_tuning(),
    }
