#include <vector>
#include <iostream>

enum color_t {
     COLOR_MIXED = -1,
     COLOR_UNKNOWN = -2,
     COLOR_DEFAULT = 0,
     COLOR_RED = 1,
     COLOR_BLUE = 2
};

typedef int amount_t;

struct Coin {
     color_t color;
     amount_t amount;
     Coin(color_t color_, amount_t amount_)
          :color(color_), amount(amount_)
          {}
};

typedef std::vector<Coin> coins;

void excerpt() {
     // we have three state variables, let's initialize them:
     cur_amount = 0; // current amount of inputs
     cur_color = COLOR_UNKNOWN; // color of those inputs
     ii = inputs.begin(); // inputs iterator

     oi = outputs.begin(); //output iterator
     for (; oi != outputs.end(); ++oi) { // go through all outputs
          want_amount = oi->amount; // amount of output we're matching
          
          // eat inputs if needed
          while ((cur_amount < want_amount) // do we need more?
                 && 
                 (ii != inputs.end())) // have we reached the end?
          {   // eat input pointed to by iterator

               if (cur_amount == 0) // brand new color stripe
                    cur_color = ii->color;
               else if (cur_color != ii->color)
                    // if we already have some, we need to check whether 
                    // coins are of same color. if they are not, they are
                    // mixed
                    cur_color = COLOR_MIXED;
               
               cur_amount += ii->amount; // add to out amount
               ++ii; // and go to next input          
          }

          if (cur_amount < want_amount)
               // we could not get enough from inputs
               // transaction is invalid if sum(inputs) > sum(outputs)
               return false;     

          oi->color = cur_color; // assign color to output
          cur_amount -= oi->amount; // decrease current amount by sum we've used
     }
}

bool compute_txn_colors(const coins& inputs, coins& outputs) {
     color_t cur_color = COLOR_UNKNOWN;
     amount_t cur_amount = 0;
     coins::const_iterator ii = inputs.begin();

     // color outputs one by one
     for (coins::iterator oi = outputs.begin(); oi != outputs.end(); ++oi) {
          int want_amount = oi->amount;
          
          // go through inputs until we have enough value
          while ((cur_amount < want_amount) && (ii != inputs.end())) {
               std::cout << "State: color:"<< cur_color << ", amount:" << cur_amount << std::endl;
               std::cout << "Eating (c:" << ii->color << ",a:" << ii->amount << ") to match " <<
                    "(c:" << oi->color << ",a:" << oi->amount << ") " << std::endl;

               if (cur_amount == 0) 
                    cur_color = ii->color;
               else if (cur_color != ii->color)
                    cur_color = COLOR_MIXED;
               
               cur_amount += ii->amount;
               ++ii;
          }

          if (cur_amount < want_amount)
               //transaction is invalid if sum(inputs) > sum(outputs)
               return false;     
          
          oi->color = cur_color;
          cur_amount -= oi->amount;
     }
     return true;
}

void print_coins(const coins& coinz) {
     for (coins::const_iterator oi = coinz.begin(); oi != coinz.end(); ++oi)
          std::cout << "Color: " << oi->color << " amount: " << oi->amount << std::endl;
}

void read_coins(coins& coinz) {
     size_t coin_count;
     std::cin >> coin_count;
     for (; coin_count > 0; --coin_count) {
          int c;
          amount_t a;
          std::cin >> c >> a;
          coinz.push_back(Coin((color_t)c, a));
     }
}

int main(int argc, char* argv[]) {
     coins inputs, outputs;
     
     if (argc > 1) {
          read_coins(inputs);
          read_coins(outputs);
     } else {
          // Example:
          inputs.push_back(Coin(COLOR_RED, 1));
          inputs.push_back(Coin(COLOR_RED, 2));
          inputs.push_back(Coin(COLOR_BLUE, 1));
          inputs.push_back(Coin(COLOR_DEFAULT, 4));
          
          outputs.push_back(Coin(COLOR_UNKNOWN, 3));
          outputs.push_back(Coin(COLOR_UNKNOWN, 1));
          outputs.push_back(Coin(COLOR_UNKNOWN, 3));
     }

     std::cout << "inputs:" << std::endl;
     print_coins(inputs);
     std::cout << "Outputs:" << std::endl;
     print_coins(outputs);     

     std::cout << "Coloring log:" << std::endl;
     bool result = compute_txn_colors(inputs, outputs);

     std::cout << "Outputs colored:" << std::endl;
     print_coins(outputs);

     if (!result)
          std::cout << "Invalid transaction!" << std::endl;

     return 0;
}
