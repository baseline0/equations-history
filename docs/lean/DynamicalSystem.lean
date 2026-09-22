/-
  DynamicalSystem: Abstract formalization of dynamical systems

  A dynamical system consists of:
  - State space (what the system is at any moment)
  - Input space (external signals that influence the system)
  - Output space (what we observe or measure)
  - State evolution (how state changes over time)
  - Output map (how to read measurements from state)

  This is the foundation for proving structural equivalence across domains.
  Source: equations-history Phase 4 formalization
-/

import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Basic

namespace DynamicalSystem

/- State-space representation of a linear time-invariant system
   ẋ = A·x + B·u
   y = C·x + D·u
-/
structure LinearTI (n m p : ℕ) where
  A : Matrix (Fin n) (Fin n) ℝ
  B : Matrix (Fin n) (Fin m) ℝ
  C : Matrix (Fin p) (Fin n) ℝ
  D : Matrix (Fin p) (Fin m) ℝ

/- Second-order normalized form
   ξ̈ + 2ζω₀·ξ̇ + ω₀²·ξ = u
   where ζ is damping ratio, ω₀ is natural frequency
-/
structure NormalizedSecondOrder where
  ω₀_sq : ℝ      -- Natural frequency squared (ω₀²)
  ζ : ℝ          -- Damping ratio (ζ)

  -- Constraints
  ω₀_sq_pos : ω₀_sq > 0
  ζ_nonneg : ζ ≥ 0

/- Two linear systems are state-space equivalent if there exists
   an invertible state transformation T such that:
   - T(f₁(x, u)) = f₂(T(x), u)  [state evolution preserved]
   - g₁(x, u) = g₂(T(x), u)     [outputs identical]
-/
def StateSpaceEquivalent
    (sys1 sys2 : LinearTI 2 1 1) : Prop :=
  ∃ (T : Matrix (Fin 2) (Fin 2) ℝ),
    IsUnit T.det ∧  -- T is invertible
    -- State evolution is preserved: A₂·T = T·A₁
    sys2.A * T = T * sys1.A ∧
    -- Input transformation: B₂ = T·B₁
    sys2.B = T * sys1.B ∧
    -- Output is identical: C₂·T = C₁
    sys2.C * T = sys1.C ∧
    -- Direct feedthrough: D₂ = D₁
    sys2.D = sys1.D

/- Convert a second-order normalized form to state-space
   State: x = [ξ, ξ̇]ᵀ
   Dynamics:
     ẋ₁ = x₂
     ẋ₂ = -ω₀²·x₁ - 2ζω₀·x₂ + u
   Output: y = x₁ (observe position)
-/
def normalizedToStateSpace (norm : NormalizedSecondOrder) : LinearTI 2 1 1 :=
  let A : Matrix (Fin 2) (Fin 2) ℝ := fun i j =>
    if i = 0 ∧ j = 1 then 1         -- ẋ₁ = x₂
    else if i = 1 ∧ j = 0 then -norm.ω₀_sq  -- ẋ₂ = -ω₀²·x₁
    else if i = 1 ∧ j = 1 then -2 * norm.ζ * Real.sqrt norm.ω₀_sq  -- -2ζω₀·x₂
    else 0
  let B : Matrix (Fin 2) (Fin 1) ℝ := fun i j =>
    if i = 1 then 1 else 0           -- u only affects ẋ₂
  let C : Matrix (Fin 1) (Fin 2) ℝ := fun i j =>
    if i = 0 ∧ j = 0 then 1 else 0  -- y = x₁
  let D : Matrix (Fin 1) (Fin 1) ℝ := fun i j => 0  -- No feedthrough
  ⟨A, B, C, D⟩

end DynamicalSystem
