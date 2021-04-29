import car
import simulations


class Simulation(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Simulation")

    @car.command()
    async def akpull(
        self, ctx,
        pulls: car.to_int() // (
            "The amount of pulls to pull"
            ),
        *,
        ore: car.to_int() // (
            "The amount of originite to use for pulls"
            ) = 0,
        pullcost: car.to_int() // (
            "The amount of originite required to buy a pull"
            ) = 600,
        probge5: car.to_float() // (
            "The base probability of getting >=5\\*s"
            ) = 0.1,
        probge6: car.to_float() // (
            "The base probability of getting >=6\\*s"
            ) = 0.02,
        pity6inc: car.to_float() // (
            "The amount to increase during 6\\* pity"
            ) = 0.02,
        prob5rateup: car.to_float() // (
            "The probability of a 5\\* operator being rate-up"
            ) = 0.5,
        prob6rateup: car.to_float() // (
            "The probability of a 6\\* operator being rate-up"
            ) = 0.5,
        pity5: car.to_int() // (
            "The amount of pulls that guarantees at least a 5\\*"
            ) = 10,
        pity6: car.to_int() // (
            "The amount of pulls before 6\\* pity kicks in"
            ) = 50,
        size5pool: car.to_int() // (
            "The size of the 5\\* rate-up pool"
            ) = 3,
        size6pool: car.to_int() // (
            "The size of the 6\\* rate-up pool"
            ) = 2,
        since5: car.to_int() // (
            "The amount of pulls since the last 5*"
            ) = 0,
        since6: car.to_int() // (
            "The amount of pulls since the last 6*"
            ) = 0
        ):
        """
        Simulates Arknights pulls
        """
        pulls += int(ore/pullcost)
        times = min(1000000, int(20000000/pulls))

        results = simulations.ak_pull(
            times,
            pulls,
            prob_ge5=probge5,
            prob_ge6=probge6,
            pity6_inc=pity6inc,
            prob_5rateup=prob5rateup,
            prob_6rateup=prob6rateup,
            pity5=pity5,
            pity6=pity6,
            size_5pool=size5pool,
            size_6pool=size6pool,
            since5=since5,
            since6=since6
        )
        r = [["" for _ in range(8)] for _ in range(6)]
        for i in range(6):
            r[i][0] = f" {results[i][0]:6.2f}"
            for j in range(1, 8):
                r[i][j] = f"{100*results[i][j]:6.1f}%"
        s = (
             "```css\n"
            f"Pulls: {pulls}, 5* pity: {since5}/{pity5}, 6* pity: {since6}/"
            f"{pity6}, Simulations: {times}\n\nP(≥5*): {probge5}, "
            f"P(6*): {probge6}, 6* Pity Increment: {pity6inc}, P(Rate-up | 5*)"
            f": {prob5rateup}, P(Rate-up | 6*): {prob6rateup}, 5* Rate-up pool"
            f" size: {size5pool}, 6* Rate-up pool size: {size6pool}\n\n"
             "[5*]  Any      Rate-up  Specific\n"
            f"Ex. {r[0][0]}  {r[1][0]}  {r[2][0]}\n"
            f" 0x {r[0][1]}  {r[1][1]}  {r[2][1]}\n"
            f" 1x {r[0][2]}  {r[1][2]}  {r[2][2]}\n"
            f" 2x {r[0][3]}  {r[1][3]}  {r[2][3]}\n"
            f" 3x {r[0][4]}  {r[1][4]}  {r[2][4]}\n"
            f" 4x {r[0][5]}  {r[1][5]}  {r[2][5]}\n"
            f" 5x {r[0][6]}  {r[1][6]}  {r[2][6]}\n"
            f"≥6x {r[0][7]}  {r[1][7]}  {r[2][7]}\n"
             "[6*]  Any      Rate-up  Specific\n"
            f"Ex. {r[3][0]}  {r[4][0]}  {r[5][0]}\n"
            f" 0x {r[3][1]}  {r[4][1]}  {r[5][1]}\n"
            f" 1x {r[3][2]}  {r[4][2]}  {r[5][2]}\n"
            f" 2x {r[3][3]}  {r[4][3]}  {r[5][3]}\n"
            f" 3x {r[3][4]}  {r[4][4]}  {r[5][4]}\n"
            f" 4x {r[3][5]}  {r[4][5]}  {r[5][5]}\n"
            f" 5x {r[3][6]}  {r[4][6]}  {r[5][6]}\n"
            f"≥6x {r[3][7]}  {r[4][7]}  {r[5][7]}\n"
            "```"
        )

        await ctx.send(s);

