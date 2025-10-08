using Godot;
using System;

public partial class Rui : Node3D
{
    [Export] private AnimationTree Animator;
    [Export] private float blend_speed = 1;
    private float MoveVal = 0;
    
    public override void _Ready()
    {
        UpdateBlendTree();
    }

    public override void _Process(double delta)
    {
        if (InterfaceManager.instance.Menu.following && InterfaceManager.instance.Menu.MouseMoving && MoveVal < 1)
        {
            MoveVal += (float)delta * blend_speed;
        }
        else if (MoveVal > 0)
        {
            MoveVal -= (float)delta * blend_speed;
        }
        
        UpdateBlendTree();
    }

    private void UpdateBlendTree()
    {
        ;
        Animator.Set("parameters/Run/blend_amount", MoveVal);
    }
}
