using System;
using System.Reflection;

class Program {
    static void Main() {
        var asm = Assembly.LoadFrom("GrandLarcenyAuto.dll");
        
        var playerStateType = asm.GetType("GrandLarcenyAuto.PlayerState")!;
        var vaultType = asm.GetType("GrandLarcenyAuto.SafehouseVault")!;
        
        var player = Activator.CreateInstance(playerStateType)!;
        var wantedStarsProp = playerStateType.GetProperty("WantedStars")!;
        
        // Set WantedStars to EXACTLY 6
        wantedStarsProp.SetValue(player, 6);
        
        // Instantiate vault with the player state
        var vault = Activator.CreateInstance(vaultType, player)!;
        var result = vaultType.GetMethod("TryOpen")!.Invoke(vault, null);
        
        Console.WriteLine("\n==========================================");
        Console.WriteLine(result);
        Console.WriteLine("==========================================\n");
    }
}
