import simulations


print(simulations.ak_pull(100, 60, prob_ge5=0.1, prob_ge6=0.02,
    pity6_inc=0.02, prob_5rateup=0.5, prob_6rateup=0.5, pity5=10,
    pity6=50, size_5pool=3, size_6pool=2))
