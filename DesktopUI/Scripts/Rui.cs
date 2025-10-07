using Godot;
using System;

public partial class Rui : Node3D
{
    [Export] private AnimationPlayer Animator;
    
    public override void _Ready()
    {
        Animator.Play("Idle");
    }
}
