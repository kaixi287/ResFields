import torch

class Linear(torch.nn.Linear):
    r"""Applies a ResField Linear transformation to the incoming data: :math:`y = x(A + \delta A_t)^T + b`

    Args:
        in_features: size of each input sample
        out_features: size of each output sample
        bias: If set to ``False``, the layer will not learn an additive bias.
            Default: ``True``
        rank: value for the the low rank decomposition
        capacity: size of the temporal dimension

    Attributes:
        weight: (F_out x F_in)
        bias:   the learnable bias of the module of shape :math:`(\text{out\_features})`.

    Examples::

        >>> m = nn.Linear(20, 30, rank=10, capacity=100)
        >>> input_x, input_time = torch.randn(128, 20), torch.randn(128)
        >>> output = m(input, input_time)
        >>> print(output.size())
        torch.Size([128, 30])
    """

    def __init__(self, in_features: int, out_features: int, bias: bool = True,
                 device=None, dtype=None, rank=0, capacity=0, mode='lookup') -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert mode in ['lookup', 'interpolation']
        self.rank = rank
        self.capacity = capacity
        self.mode = mode

        if self.rank > 0 and self.capacity > 0:
            self.register_parameter('weights_t', torch.nn.Parameter(0.01*torch.randn((self.capacity, self.rank)))) # C, R
            self.register_parameter('matrix_t', torch.nn.Parameter(0.01*torch.randn((self.rank, self.weight.shape[0]*self.weight.shape[1])))) # R, F_out*F_in

    def _get_delta_weight(self, input_time=None, frame_id=None):
        """Returns the delta weight matrix for a given time index.
        
        Args:
            input_time: time index of the input tensor. Data range from -1 to 1. 
                Tensor of shape (N)
        Returns:
            delta weight matrix of shape (N, F_out, F_in)
        """
        # return self.weight + torch.einsum('tr,rfi->tfi', self.weights_t, self.matrix_t)
        delta_w = (self.weights_t @ self.matrix_t).t() + self.weight.view(-1, 1) # F_out*F_in, C
        if self.mode == 'interpolation':
            grid_query = input_time.view(1, -1, 1, 1) # 1, N, 1, 1

            out = torch.nn.functional.grid_sample(
                delta_w.unsqueeze(0).unsqueeze(-1), # 1, F_out*F_in, C, 1
                torch.cat([torch.zeros_like(grid_query), grid_query], dim=-1), 
                padding_mode='border', 
                mode='nearest',
                align_corners=True
            ) # 1, F_out*F_in, N, 1
            out = out.view(*self.weight.shape, grid_query.shape[1]).permute(2, 0, 1) # F_out, F_in, N
        elif self.mode == 'lookup':
            out = delta_w.permute(1, 0).view(-1, *self.weight.shape)[frame_id] # N, F_out, F_in
        return out # N, F_out, F_in

    def forward(self, input: torch.Tensor, input_time=None, frame_id=None) -> torch.Tensor:
        """Applies the linear transformation to the incoming data: :math:`y = x(A + \delta A_t)^T + b
        
        Args:
            input: (B, S, F_in)
            input_time: time index of the input tensor. Data range from -1 to 1.
                Tensor of shape (B) or (1)
        Returns:
            output: (B, S, F_out)
        """
        if self.rank == 0 or self.capacity == 0:
            return torch.nn.functional.linear(input, self.weight, self.bias)

        assert input_time is not None, "time must be provided for ResField"

        weight = self._get_delta_weight(input_time, frame_id) # B, F_out, F_in
        if weight.shape[0] == 1 or len(weight.shape) == 2:
            return torch.nn.functional.linear(input, weight.squeeze(0), self.bias)
        else:
            # (B, F_out, F_in) x (B, F_in, S) -> (B, F_out, S)
            return (weight @ input.permute(0, 2, 1) + self.bias.view(1, -1, 1)).permute(0, 2, 1) # B, S, F_out

    def extra_repr(self) -> str:
        return 'in_features={}, out_features={}, bias={}, rank={}, capacity={}, mode={}'.format(
            self.in_features, self.out_features, self.bias is not None, self.rank, self.capacity, self.mode
        )
