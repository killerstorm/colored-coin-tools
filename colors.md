Colored coins
=============

Overview
--------

"Colored coins" is a scheme which allows one to assign labels ("colors") to transction outputs ("coins") in such a way that this assignment maintains useful properties:

 * it is possible to assign such labels automatically up from a starting configuration
 * there is a "rule of conservation" for colored coins: amount of coins of each distinct color is preserved in transaction (with few exceptions)

These properties allow one to use colored coins as if they were separate currency or asset type.

There are several proposed coloring schemes, one described here is known as "order-based weak coloring". 

Recursive color tracking
------------------------

Transaction output is recognized as colored when it can be unambiguously traced down to color-issuing transaction outputs, which are colored by definition.

Formally: In a single transaction, transaction output is of color X when all matching inputs are of color X. Input is of color X if output it spends is of color X.

Thus to find color of a transaction output we can perform a recursive traversal of transaction graph until we get to transaction output which are colored via definition, or we get to coinbase transaction which creates fresh uncolored coins.

However, this is just a definition of coloring. Although a "colored coin client" can implement this recursive traversal literally, there is a variety of implementation strategies which offer different performance trade-offs.

For example, it is possible to scan blockchain sequentially from the start, noting all colored transactions. It is possible because we can compute colors for each individual transaction independently as long as we know input colors, and if we scan transactions sequentially we always know colors of inputs by the time transaction is considered.

Order-based coloring
--------------------

Definition above left "matching" undefined. In order-based coloring inputs and outputs are matched according to the order they appear in transaction.

To visualize this matching, imagine that each input and output is represented with a box with height proportional to number of coins in that input/output. We stack this boxes on top of each other in same order they appear in transaction. To find a color of an output box you need to check colors of input boxes which are on same height.

Here's an illustration:

      *----* *----*
      | I1 | | O1 |
      ------ ------
      | I2 | | O2 |
      ------ |    |
      | I3 | |    |
      *----* *----*

Output O1 is matched by input I1, while O2 is matched by I2 and I3.

If I2 and I3 are of same color then O2 is of that color too. Otherwise O2 is uncolored.

Formal definition:

Preceding sum of input i is sum of values of all outputs from 0 below i. `PS(input[i]) = sum(input[x].value, x=0..(i-1))`
Preceding sum of output j is sum of values of all outputs from 0 below j. `PS(output[j]) = sum(output[x].value, x=0..(j-1))`

Input i matches output j when segments `[PS(input[i]), PS(input[i])+input[i].value]` and `[PS(output[j]), PS(output[j])+output[j].value]` overlap.

I.e. `PS(input[i]) < PS(output[j])+output[j].value` and `PS(input[i])+input[i].value] > PS(output[j])`.

If we want to compute colors of all outputs in a transaction, we can simply go through all outputs one by one, in order they appear in transction, and for each output 'eat' enough inputs to cover it. If all eaten inputs are of same color then output is of that color too. Otherwise output is uncolored.

We need to maintain three state variables during iteration over outputs:

1. i -- index of current input to be eaten
2. `current_amount` -- remaining sum in inputs eaten so far
3. color -- color if inputs we have eaten

To eat an input we increase `current_amount`, update color (check whether it is same as color of inputs eaten before), and increment i.

Once we have eaten enough inputs we can color an output and decrease current amount by value of that output. If `current_amount` is zero we reset color.

Here is a reference implementation if this algorithm: https://github.com/killerstorm/colored-coin-tools/blob/master/color.js

Function `computer_colors` performs color computation for one transaction. The rest are validation functions. (See below.)

Note that this function also implements coloring of zero-valued outputs, without support for them it would be considerably shorter.

Zero-valued outputs (optional)
------------------------------

Some smart property proposals advocated use of zero-valued outputs to denote ownership of a property. We currently do not recommend using them as it is usually not a problem to use at least 1 satoshi for a colored transaction output. But we want to make our algorithms compatible with such use.

Zero-valued outputs can violate conservation rule (i.e. they can appear in any number), and so we cannot use matching rule above.

Instead we use a separate rule which works for zero-valued outputs: 

Zero-valued output can be matched by zero-valued inputs at same preceding sum, i.e. output j can be matched by input i if `PS(input[i]) = PS(output[j])`.

If there is a single input and single output having that preceding sum, they match each other.

Otherwise we match inputs/outputs at same preceding sum ("height") one-to-one, in order they appear in transaction, removing matching inputs/outputs from consideration. If there is no matching input output is considered uncolored. Likewise inputs without matching outputs are simply ignored.

Function `compute_colors` mentioned above implements coloring of zero-valued outputs within a single transaction.

Rules for well-formed colored coin transactions
-----------------------------------------------

One transaction can include coins of different colors. This might be useful, particularly, for 'atomic coin swapping': a transaction which trades colored coins of one user for colored coins of another user.

Rules listed above allow one to preserve color labels even if some of parties involved have only partial information about colors involved. It is recommened for colored coin software to follow these rules, although it is not strictly necessary:

1. All inputs and outputs should be sorted by color, with matching sort order. E.g. red inputs, blue inputs, uncolored inputs. Red outputs, blue outputs, uncolored outputs.
2. All uncolored inputs/outputs should go after all colored inputs/outputs.
3. Fee should be paid using uncolored coins. If it is absolutely necessary to pay fee with colored coins, that color should go the last.
4. Total value of coins of each color should be preserved.

Color definitions
-----------------

We want to give users an ability to issue coloring coins as they want. To issue coins client software should prepare a transaction with output having a desired number of satoshis, and then it should prepare a color definition file. Color definition includes:

 * an identifier of a color, a 256-bit hash
 * desired display name
 * hash of a genesis transaction
 * output index within that transaction

Client software should apply this definition to start distinguishing newly issued coins from uncolored ones. (Transaction output mentioned in definition is colored by definition, this overrides all other coloring rules.) If user wants other people to recognize these coins he should share this color definition file, for example, publishing it on some site.

It is possible that color definition would reference multiple genesis transaction outputs as user might issue colored coins in batches. (When new batch is issued everybody should update their definition.)

Alternatively, if user wants to issue coins at will, without a need to update color definition, he should specify a color definition with an issuing address. All coins spent from that address will be colored.

Formally speaking, inputs which spend coins sent to issuing color are considered colored by definition, and thus matching outputs can be colored.

All such spens must be standard transactions, otherwise it would be hard for software to recognize such spends automatically.