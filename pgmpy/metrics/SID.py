
def SID(true_model, est_model):
    sid_mat = sid_matrix(true_model, est_model)
    return int(np.sum(sid_mat))


from pgmpy.inference import CausalInference


def sid_matrix(true_model, est_model):
    p = len(true_model)
    if len(est_model) != p:
        raise ValueError("The graphs must have the same number of nodes.")
    incorrect_intervention = np.zeros((p, p))

    for i, node_i in enumerate(true_model.nodes):
        parents_i_true = true_model.get_parents(node_i)  # parents of i in trueGraph
        parents_i_est = est_model.get_parents(node_i)  # parents of i in estGraph

        for j, node_j in enumerate(true_model.nodes):
            finished = False
            if i == j:
                finished = True
                continue

            # Implement Proposition 6 for each pair of different nodes

            # True graph predicts the causal effect to be zero if there is no direct path.
            # p(x_j | do (x_i=a)) = p(x_j)
            ijGNull = False if nx.has_path(true_model, node_i, node_j) else True

            # In the estimated model, the j is parent of i. Expect zero causal effect
            ijHNull = True if node_j in parents_i_est else False

            if not ijGNull and ijHNull:
                # Note the asymmetry that (ijGNull and not ijHNull) is not necessariliy punished.
                incorrect_intervention[i][j] = 1
                finished = True
                continue

            if ijGNull and ijHNull:
                # Causal effect from i to j vanishes in reality and in the estimated model. No mistake made.
                finished = True
                continue

            if np.array_equal(parents_i_true, parents_i_est):
                # If the same parent sets, the parent adjustment implies exactly the same formula.
                finished = True
                continue

            if nx.has_path(true_model, node_i, node_j):
                """
                This tests first part of (*) in Lemma 5. Namely,
                In G, no Z ∈ Z is a descendant of any W which lies on a directed
                path from X to Y.
                """
                #
                # True children of node i, which are on a directed path to j.
                children_i_true = true_model.get_children(node_i)
                ancestors_j_true = nx.ancestors(true_model, node_j)

                children_on_directed_path = list(
                    set(ancestors_j_true).intersection(children_i_true)
                )

                # TODO: can improve with caching - ancestors and descendants sets
                for node_k in true_model.nodes:
                    for child in children_on_directed_path:
                        for z in parents_i_est:
                            if nx.has_path(true_model, child, node_k) and nx.has_path(
                                true_model, node_k, z
                            ):
                                incorrect_intervention[i][j] = 1
                                finished = True
                                continue
            if finished:
                continue

            ci = CausalInference(true_model)
            if not ci.is_valid_adjustment_set(node_i, node_j, parents_i_est):

                incorrect_intervention[i][j] += 1

    return incorrect_intervention
